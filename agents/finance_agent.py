"""
Finance Agent.
Evaluates startup unit economics, capital requirements, operating costs,
pricing models, expected revenue trajectories, and break-even points.
"""
from typing import Optional
from crewai import Agent
from config.llm_config import create_agent_llm, TokenBudgetManager


def create_finance_agent(token_manager: Optional[TokenBudgetManager] = None) -> Agent:
    """
    Instantiates the Finance Agent with centralized LLM configuration.
    """
    llm = create_agent_llm("finance", token_manager=token_manager)

    return Agent(
        role="Chief Financial Analyst",
        goal=(
            "Model realistic startup unit economics, capital requirements, operating costs, "
            "pricing tiers, revenue projections, and break-even points in structured JSON format."
        ),
        backstory=(
            "You are a pragmatic venture CFO and financial modeler. You calculate hard unit economics, "
            "burn rate modeling, and realistic customer acquisition economics. You provide concise, "
            "direct calculations in clean JSON without conversational chatter."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )
