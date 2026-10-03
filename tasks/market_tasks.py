"""
Market Research Task definition for CrewAI.
"""
from typing import Dict, Any
from crewai import Task, Agent


def create_market_research_task(
    agent: Agent,
    startup_data: Dict[str, Any],
    rag_context: str = "",
) -> Task:
    """
    Creates the CrewAI task for market research.
    """
    description = f"""
Conduct an in-depth market research analysis for the following startup venture:

Startup Name: {startup_data.get('name', 'Venture')}
Idea: {startup_data.get('idea', '')}
Country/Region: {startup_data.get('country', 'Global')}
Target Market: {startup_data.get('target_market', 'General')}
Target Customer: {startup_data.get('target_customer', 'Consumers')}
Initial Budget: {startup_data.get('currency', '$')}{startup_data.get('budget', 0):,}
Founder Experience: {startup_data.get('founder_experience', 'Beginner')}
Additional Context: {startup_data.get('additional_context', 'None')}

{rag_context}

Analyze and provide:
1. Target Customer Segments & Demographics
2. Acute Customer Problems & Unmet Needs
3. Prevailing Market & Industry Trends
4. Key Market Opportunities & Expansion Vectors
5. Direct Demand Signals & Customer Willingness-to-Pay
6. Local Geographic Market Factors for {startup_data.get('country', 'the region')}
7. Distinguish verified retrieved evidence from assumptions
8. Market Score (0-100 integer)

Format your output strictly as a valid JSON object matching this structure:
{{
  "market_score": 82,
  "target_customers": ["segment 1", "segment 2"],
  "customer_problems": ["problem 1", "problem 2"],
  "market_trends": ["trend 1", "trend 2"],
  "market_opportunities": ["opportunity 1", "opportunity 2"],
  "demand_signals": ["signal 1", "signal 2"],
  "local_market_nuances": "detailed local market context",
  "growth_potential": "High/Moderate/Niche",
  "retrieved_evidence": ["fact 1", "fact 2"],
  "assumptions": ["assumption 1", "assumption 2"],
  "market_risks": ["risk 1", "risk 2"],
  "summary": "Concise 2-sentence executive summary of the market opportunity."
}}
"""
    return Task(
        description=description,
        expected_output="A structured JSON object detailing market size, customer pain points, trends, local market factors, and market score.",
        agent=agent,
    )
