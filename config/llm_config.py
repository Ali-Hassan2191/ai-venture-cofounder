"""
Centralized LLM Configuration & Token Budget Manager.
Isolates provider-specific logic and credentials from agents, tasks, and UI.
Strictly adheres to global 7,500 output token budget across all 6 agents.
"""
import os
import logging
from typing import Dict, Any, Optional
import streamlit as st

# Fix for Groq API: Groq rejects 'cache_breakpoint' property injected into messages by CrewAI/LiteLLM
try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass

try:
    import litellm
    litellm.drop_params = True

    _orig_litellm_completion = litellm.completion
    _orig_litellm_acompletion = litellm.acompletion

    def _strip_cache_breakpoint(messages):
        if not isinstance(messages, list):
            return messages
        for m in messages:
            if isinstance(m, dict):
                m.pop("cache_breakpoint", None)
                m.pop("cache_control", None)
                if "content" in m and isinstance(m["content"], list):
                    for part in m["content"]:
                        if isinstance(part, dict):
                            part.pop("cache_breakpoint", None)
                            part.pop("cache_control", None)
        return messages

    def _safe_litellm_completion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = _strip_cache_breakpoint(kwargs["messages"])
        elif len(args) > 1 and isinstance(args[1], list):
            args = list(args)
            args[1] = _strip_cache_breakpoint(args[1])
            args = tuple(args)
        return _orig_litellm_completion(*args, **kwargs)

    async def _safe_litellm_acompletion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = _strip_cache_breakpoint(kwargs["messages"])
        elif len(args) > 1 and isinstance(args[1], list):
            args = list(args)
            args[1] = _strip_cache_breakpoint(args[1])
            args = tuple(args)
        return await _orig_litellm_acompletion(*args, **kwargs)

    litellm.completion = _safe_litellm_completion
    litellm.acompletion = _safe_litellm_acompletion
except Exception:
    pass

from crewai import LLM
from utils.constants import (
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_TOTAL_OUTPUT_TOKENS,
    DEFAULT_TOKEN_ALLOCATIONS,
)

logger = logging.getLogger(__name__)


class TokenBudgetManager:
    """
    Centralized Token Budget Manager.
    Enforces a hard GLOBAL limit of 7,500 output tokens across all 6 agents.
    Surplus tokens from efficient agents roll forward to subsequent agents (e.g. CEO synthesis).
    """

    def __init__(self, max_total_tokens: int = MAX_TOTAL_OUTPUT_TOKENS):
        self.max_total_tokens = max_total_tokens
        self.used_tokens = 0
        self.agent_allocations = dict(DEFAULT_TOKEN_ALLOCATIONS)
        self.agent_usage: Dict[str, int] = {}
        self.call_history: list = []

    @property
    def remaining_tokens(self) -> int:
        return max(0, self.max_total_tokens - self.used_tokens)

    def request_budget(self, agent_key: str) -> int:
        """
        Calculates safe max_tokens allocation for an agent call.
        Ensures the allocation never exceeds the global remaining tokens.
        """
        baseline = self.agent_allocations.get(agent_key, 1000)
        # If remaining budget is less than baseline, cap it
        allocated = min(baseline, self.remaining_tokens)
        # Minimum safety threshold to allow a concise response
        return max(150, allocated)

    def record_usage(self, agent_key: str, tokens_used: int) -> None:
        """
        Records actual tokens consumed and updates cumulative counter.
        """
        actual = max(0, tokens_used)
        self.used_tokens += actual
        self.agent_usage[agent_key] = self.agent_usage.get(agent_key, 0) + actual
        self.call_history.append({
            "agent": agent_key,
            "tokens_used": actual,
            "cumulative_used": self.used_tokens,
            "remaining": self.remaining_tokens,
        })
        logger.info(
            f"TokenBudgetManager: Agent '{agent_key}' used {actual} tokens. "
            f"Total used: {self.used_tokens}/{self.max_total_tokens}. "
            f"Remaining: {self.remaining_tokens} tokens."
        )

    def can_retry(self, min_required: int = 250) -> bool:
        """Checks if enough token budget remains to attempt a retry."""
        return self.remaining_tokens >= min_required

    def get_summary(self) -> Dict[str, Any]:
        """Returns structured diagnostic data for UI and logging."""
        return {
            "max_total_tokens": self.max_total_tokens,
            "total_used": self.used_tokens,
            "total_remaining": self.remaining_tokens,
            "usage_percent": round((self.used_tokens / self.max_total_tokens) * 100.0, 1),
            "agent_usage": dict(self.agent_usage),
            "call_history": list(self.call_history),
        }

    def reset(self) -> None:
        """Resets the budget manager for a new analysis run."""
        self.used_tokens = 0
        self.agent_usage.clear()
        self.call_history.clear()


# Global Singleton for Token Management
global_token_manager = TokenBudgetManager()


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely retrieves a configuration key from Streamlit secrets or OS environment.
    Avoids exceptions if secrets file is absent or incomplete.
    """
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.environ.get(key, default)


def get_llm_config() -> Dict[str, Any]:
    """
    Retrieves centralized LLM provider, model, and authentication settings.
    """
    provider = get_secret("LLM_PROVIDER", DEFAULT_LLM_PROVIDER).lower()
    raw_model = get_secret("LLM_MODEL", DEFAULT_LLM_MODEL)

    api_key = None
    if provider == "groq":
        api_key = get_secret("GROQ_API_KEY")
    elif provider in ("gemini", "google"):
        api_key = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
    elif provider == "openrouter":
        api_key = get_secret("OPENROUTER_API_KEY")
    else:
        api_key = get_secret("LLM_API_KEY") or get_secret("GROQ_API_KEY")

    try:
        temp = float(get_secret("TEMPERATURE", str(DEFAULT_TEMPERATURE)))
    except (ValueError, TypeError):
        temp = DEFAULT_TEMPERATURE

    return {
        "provider": provider,
        "model": raw_model,
        "api_key": api_key,
        "temperature": temp,
    }


def create_agent_llm(agent_key: str, token_manager: Optional[TokenBudgetManager] = None) -> LLM:
    """
    Creates a CrewAI LLM instance configured with the provider and the
    exact output token budget allocated to the specific agent.
    """
    mgr = token_manager or global_token_manager
    config = get_llm_config()

    provider = config["provider"]
    raw_model = config["model"]
    api_key = config["api_key"]
    temperature = config["temperature"]

    # Calculate token budget for this agent call
    max_tokens = mgr.request_budget(agent_key)

    # Format model string for CrewAI / LiteLLM provider routing
    if provider == "groq":
        if not raw_model.startswith("groq/"):
            model_identifier = f"groq/{raw_model}"
        else:
            model_identifier = raw_model
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
    elif provider in ("gemini", "google"):
        if not raw_model.startswith("gemini/"):
            model_identifier = f"gemini/{raw_model}"
        else:
            model_identifier = raw_model
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
    elif provider == "openrouter":
        if not raw_model.startswith("openrouter/"):
            model_identifier = f"openrouter/{raw_model}"
        else:
            model_identifier = raw_model
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
    else:
        model_identifier = raw_model

    return LLM(
        model=model_identifier,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )
