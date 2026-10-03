"""
Marketing & Go-To-Market Agent.
Formulates actionable customer acquisition strategies, high-conversion channels,
launch campaigns, viral growth mechanics, and customer retention loops.
"""
from typing import Optional
from crewai import Agent
from config.llm_config import create_agent_llm, TokenBudgetManager


def create_marketing_agent(token_manager: Optional[TokenBudgetManager] = None) -> Agent:
    """
    Instantiates the Marketing Agent with centralized LLM configuration.
    """
    llm = create_agent_llm("marketing", token_manager=token_manager)

    return Agent(
        role="Head of Growth & Go-To-Market",
        goal=(
            "Design a targeted, capital-efficient Go-To-Market strategy, identifying "
            "the highest-converting customer acquisition channels, compelling launch campaigns, "
            "promotional ideas, and sustainable retention mechanisms tailored to the startup idea."
        ),
        backstory=(
            "You are a growth marketing architect who has scaled multiple venture-backed platforms "
            "from zero to their first 10,000 active users. You reject generic marketing fluff in favor of "
            "hyper-targeted, unscalable early tactics, organic referral loops, and clear CAC efficiency."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
