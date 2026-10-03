"""
CEO Agent.
The final synthesis, strategy, and decision-making agent. Combines intelligence from
all five specialist co-founders to generate the unified Startup Blueprint,
objective startup scoring, holistic risk analysis, difficulty rating, and dynamic execution roadmap.
"""
from typing import Optional
from crewai import Agent
from config.llm_config import create_agent_llm, TokenBudgetManager


def create_ceo_agent(token_manager: Optional[TokenBudgetManager] = None) -> Agent:
    """
    Instantiates the CEO Decision Agent with centralized LLM configuration.
    """
    llm = create_agent_llm("ceo", token_manager=token_manager)

    return Agent(
        role="Chief Executive Officer & Lead Co-Founder",
        goal=(
            "Synthesize specialist findings from Market Research, Competitor Analysis, Finance, "
            "Marketing, and CTO co-founders. Deliver an authoritative venture evaluation, category scores, "
            "thorough risk analysis, difficulty classification, and a dynamic execution roadmap tailored to the startup."
        ),
        backstory=(
            "You are a visionary, battle-tested venture CEO and startup investor. You synthesize cross-functional "
            "signals across product, finance, tech, and marketing to make definitive strategic decisions. "
            "You provide transparent, evidence-based reasoning, realistic milestones, and candid feedback on feasibility."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
