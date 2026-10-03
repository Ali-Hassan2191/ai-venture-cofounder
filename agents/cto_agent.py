"""
CTO Agent.
Architects technical infrastructure, software engineering roadmap,
database schema, AI integration components, core product features, and technical risk mitigation.
"""
from typing import Optional
from crewai import Agent
from config.llm_config import create_agent_llm, TokenBudgetManager


def create_cto_agent(token_manager: Optional[TokenBudgetManager] = None) -> Agent:
    """
    Instantiates the CTO Agent with centralized LLM configuration.
    """
    llm = create_agent_llm("cto", token_manager=token_manager)

    return Agent(
        role="Chief Technology Officer",
        goal=(
            "Formulate a production-grade technical architecture, define core product features "
            "for the initial launch, select a scalable modern technology stack, design data architecture, "
            "and identify technical risks and security safeguards within budget constraints."
        ),
        backstory=(
            "You are an accomplished startup CTO and systems architect. You prioritize speed-to-market, "
            "robust modular architecture, and maintainable engineering practices. You balance cutting-edge "
            "AI capabilities with pragmatic operational simplicity and strict cost control."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
