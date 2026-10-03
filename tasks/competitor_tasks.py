"""
Competitor Analysis Task definition for CrewAI.
"""
from typing import Dict, Any
from crewai import Task, Agent


def create_competitor_task(
    agent: Agent,
    startup_data: Dict[str, Any],
    market_summary: str = "",
    rag_context: str = "",
) -> Task:
    """
    Creates the CrewAI task for competitor intelligence.
    """
    description = f"""
Conduct competitive intelligence analysis for:

Startup Name: {startup_data.get('name', 'Venture')}
Idea: {startup_data.get('idea', '')}
Country/Region: {startup_data.get('country', 'Global')}
Target Market: {startup_data.get('target_market', 'General')}
Market Context: {market_summary}

{rag_context}

Analyze existing direct and indirect players in this market space.
Do not fabricate non-existent facts; state clearly if competitors are local analogs or global alternatives.

Provide:
1. Realistic Top Competitors (direct and indirect)
2. Products and Services offered
3. Estimated Pricing structures
4. Strengths & Vulnerabilities/Weaknesses
5. Target Customers of each competitor
6. Market Positioning analysis
7. Critical Market Gaps that our startup can exploit
8. Defensible Unique Selling Proposition (USP)
9. Competition Score (0-100 integer, where higher indicates greater differentiation/advantage)

Format your output strictly as a valid JSON object matching this structure:
{{
  "competition_score": 75,
  "competitors": [
    {{
      "name": "Competitor Name",
      "type": "Direct / Indirect",
      "products_services": "Core offering",
      "pricing": "Pricing model or estimate",
      "strengths": ["strength 1", "strength 2"],
      "weaknesses": ["weakness 1", "weakness 2"],
      "target_customers": "Customer segment"
    }}
  ],
  "market_positioning": "Strategic positioning statement",
  "market_gaps": ["unaddressed gap 1", "gap 2"],
  "recommended_usp": "Clear defensible USP",
  "summary": "Concise 2-sentence executive summary of competitive landscape and defensibility."
}}
"""
    return Task(
        description=description,
        expected_output="A structured JSON object detailing competitors, pricing models, weaknesses, positioning, and market gaps.",
        agent=agent,
    )
