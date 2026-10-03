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
            "Model realistic startup unit economics, initial capital requirements, "
            "ongoing operational expenses, viable pricing structures, revenue projections, "
            "and break-even thresholds based on empirical benchmarks and budget constraints."
        ),
        backstory=(
            "You are a pragmatic venture CFO and financial modeler. You test business viability "
            "through hard unit economics, burn rate modeling, and realistic customer acquisition economics. "
            "You clearly distinguish verified founder budget constraints, modeled estimates, and key financial risks."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
