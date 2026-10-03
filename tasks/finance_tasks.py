"""
Financial Modeling Task definition for CrewAI.
"""
from typing import Dict, Any
from crewai import Task, Agent


def create_finance_task(
    agent: Agent,
    startup_data: Dict[str, Any],
    market_summary: str = "",
    competitor_summary: str = "",
    rag_context: str = "",
) -> Task:
    """
    Creates the CrewAI task for financial evaluation.
    """
    currency = startup_data.get("currency", "$")
    budget = startup_data.get("budget", 0)

    context_section = (
        f"\nEmpirical Financial & Unit Economics Benchmarks (from Knowledge Base):\n{rag_context}\n"
        if rag_context
        else ""
    )

    description = f"""
Build a financial model and unit economics evaluation for:

Startup Name: {startup_data.get('name', 'Venture')}
Idea: {startup_data.get('idea', '')}
Country/Region: {startup_data.get('country', 'Global')}
Available Budget: {currency}{budget:,}
Market Insights: {market_summary}
Competitive Pricing Context: {competitor_summary}
{context_section}

Calculate and evaluate:
1. Initial Capital / Investment required for initial product release
2. Monthly Operating Costs (broken down into hosting, operations, overhead)
3. Initial Software Development Costs
4. Monthly Marketing / Customer Acquisition Budget
5. Recommended Pricing Options (tiers, pricing mechanism, target margins)
6. Revenue Model (subscriptions, commissions, transaction fees, freemium)
7. Expected Revenue Projections (Year 1 benchmark scenarios)
8. Realistic Break-even Threshold (in customer units, monthly transactions, or months)
9. Clear Financial Assumptions vs. Verified Inputs
10. Finance Score (0-100 integer, assessing capital efficiency and unit profitability)

Format your output strictly as a valid JSON object matching this structure:
{{
  "finance_score": 68,
  "currency": "{currency}",
  "initial_investment_required": 25000,
  "development_costs": 12000,
  "monthly_operating_costs": 1800,
  "monthly_marketing_costs": 1500,
  "pricing_options": [
    {{
      "tier_name": "Standard",
      "price": 19.99,
      "billing_period": "monthly",
      "target_persona": "Core user"
    }}
  ],
  "revenue_model": "SaaS Subscription + 2% transaction fee",
  "projected_monthly_revenue_m6": 8500,
  "projected_annual_revenue_y1": 95000,
  "break_even_point": "450 active subscribers or 1,200 orders/month",
  "runway_months_with_budget": 8,
  "financial_assumptions": ["assumption 1", "assumption 2"],
  "financial_risks": ["risk 1", "risk 2"],
  "summary": "Concise 2-sentence executive summary of financial viability and unit economics."
}}
"""
    return Task(
        description=description,
        expected_output="A structured JSON object with capital requirements, operating costs, pricing tiers, break-even targets, and finance score.",
        agent=agent,
    )
