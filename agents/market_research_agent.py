"""
Market Research Agent.
Studies market size, target customer segments, customer problems, industry trends,
opportunities, demand signals, and local geographic nuances.
"""
from typing import Optional
from crewai import Agent
from config.llm_config import create_agent_llm, TokenBudgetManager


def create_market_research_agent(token_manager: Optional[TokenBudgetManager] = None) -> Agent:
    """
    Instantiates the Market Research Agent with centralized LLM configuration.
    """
    llm = create_agent_llm("market_research", token_manager=token_manager)

    return Agent(
        role="Chief Market Research Strategist",
        goal=(
            "Conduct rigorous, evidence-based market research on the startup idea, "
            "identifying target demographics, acute customer pain points, market trends, "
            "demand signals, and local market factors. Distinguish verified facts from assumptions."
        ),
        backstory=(
            "You are a seasoned venture research director with deep expertise in identifying "
            "underserved market niches, sizing TAM/SAM/SOM, evaluating customer willingness to pay, "
            "and diagnosing localized market dynamics. You operate strictly with intellectual honesty, "
            "clearly separating retrieved empirical evidence from working hypotheses."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
