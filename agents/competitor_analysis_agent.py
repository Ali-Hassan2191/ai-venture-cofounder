"""
Competitor Analysis Agent.
Analyzes direct and indirect competitors, offerings, pricing structures,
strengths, vulnerabilities, market positioning, and unaddressed market gaps.
"""
from typing import Optional
from crewai import Agent
from config.llm_config import create_agent_llm, TokenBudgetManager


def create_competitor_agent(token_manager: Optional[TokenBudgetManager] = None) -> Agent:
    """
    Instantiates the Competitor Intelligence Agent with centralized LLM configuration.
    """
    llm = create_agent_llm("competitor_analysis", token_manager=token_manager)

    return Agent(
        role="Competitive Intelligence Lead",
        goal=(
            "Thoroughly analyze direct and indirect competitors in the target space, "
            "evaluating their offerings, pricing tiers, strengths, weaknesses, positioning, "
            "and identifying high-value market gaps and differentiation vectors."
        ),
        backstory=(
            "You are an elite competitive intelligence specialist who dissects startup ecosystems. "
            "You reveal competitor blindspots, pricing inefficiencies, and defensible moats. "
            "You never fabricate non-existent facts; when data is unverified, you explicitly label it "
            "as an estimate or competitive proxy."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
