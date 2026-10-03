"""
Financial Modeling Task definition for CrewAI.
Ensures deterministic calculation validation and concise structured JSON outputs.
"""
from typing import Dict, Any
from crewai import Task, Agent


def enrich_financial_model(data: Dict[str, Any], budget: float) -> Dict[str, Any]:
    """
    Validates and deterministically calculates financial metrics from LLM assumptions.
    Guarantees consistent unit economics and runway calculations.
    """
    res = dict(data) if isinstance(data, dict) else {}
    monthly_ops = float(res.get("monthly_operating_costs", 1500) or 1500)
    monthly_mkt = float(res.get("monthly_marketing_costs", 1000) or 1000)
    total_burn = monthly_ops + monthly_mkt

    # Deterministic runway calculation
    if budget > 0 and total_burn > 0:
        res["runway_months_with_budget"] = round(budget / total_burn, 1)
    elif "runway_months_with_budget" not in res:
        res["runway_months_with_budget"] = 6.0

    # Ensure finance score is bounded
    score = res.get("finance_score", 70)
    try:
        res["finance_score"] = max(10, min(95, int(score)))
    except (ValueError, TypeError):
        res["finance_score"] = 70

    return res


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
    try:
        budget = float(startup_data.get("budget", 0) or 0)
    except (ValueError, TypeError):
        budget = 25000.0

    context_section = (
        f"\nEmpirical Benchmarks (from Knowledge Base):\n{rag_context}\n"
        if rag_context
        else ""
    )

    description = f"""
Model unit economics and capital requirements for:
Startup Name: {startup_data.get('name', 'Venture')}
Idea: {startup_data.get('idea', '')}
Country/Region: {startup_data.get('country', 'Global')}
Available Budget: {currency}{budget:,.0f}
Market Context: {market_summary}
Competitive Pricing Context: {competitor_summary}
{context_section}

Calculate directly:
1. Initial Capital Required for MVP release
2. Monthly Operating Costs (hosting, operations, tools)
3. Initial Software Development Costs
4. Monthly Customer Acquisition / Marketing Budget
5. Recommended Pricing Tiers (tier_name, price, billing_period, target_persona)
6. Revenue Model (subscriptions, commissions, transaction fees)
7. Expected Revenue Projections (Month 6 monthly run-rate, Year 1 annual revenue)
8. Realistic Break-even Threshold (in active subscribers or monthly orders)
9. Clear Financial Assumptions vs. Verified Constraints
10. Finance Score (0-100 integer, capital efficiency and margin health)

IMPORTANT: Output ONLY the valid JSON object below. Do NOT include conversational commentary or markdown prose before or after the JSON.

```json
{{
  "finance_score": 72,
  "currency": "{currency}",
  "initial_investment_required": 20000,
  "development_costs": 12000,
  "monthly_operating_costs": 1500,
  "monthly_marketing_costs": 1200,
  "pricing_options": [
    {{
      "tier_name": "Starter",
      "price": 29.00,
      "billing_period": "monthly",
      "target_persona": "Core customer"
    }}
  ],
  "revenue_model": "Monthly SaaS subscription",
  "projected_monthly_revenue_m6": 8500,
  "projected_annual_revenue_y1": 95000,
  "break_even_point": "350 active paying customers",
  "runway_months_with_budget": 8.5,
  "financial_assumptions": ["Assumption 1", "Assumption 2"],
  "financial_risks": ["Risk 1", "Risk 2"],
  "summary": "Executive summary of financial viability and unit economics."
}}
```
"""
    return Task(
        description=description.strip(),
        expected_output="A structured JSON object with capital requirements, operating costs, pricing tiers, break-even targets, and finance score.",
        agent=agent,
    )
