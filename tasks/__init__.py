"""
Tasks package initialization.
Exports task generator functions for all 6 AI co-founders.
"""
from tasks.market_tasks import create_market_research_task
from tasks.competitor_tasks import create_competitor_task
from tasks.finance_tasks import create_finance_task
from tasks.marketing_tasks import create_marketing_task
from tasks.cto_tasks import create_cto_task
from tasks.ceo_tasks import create_ceo_synthesis_task

__all__ = [
    "create_market_research_task",
    "create_competitor_task",
    "create_finance_task",
    "create_marketing_task",
    "create_cto_task",
    "create_ceo_synthesis_task",
]
