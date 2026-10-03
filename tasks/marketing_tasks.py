"""
Marketing & Go-To-Market Task definition for CrewAI.
"""
from typing import Dict, Any
from crewai import Task, Agent


def create_marketing_task(
    agent: Agent,
    startup_data: Dict[str, Any],
    market_summary: str = "",
    competitor_summary: str = "",
    finance_summary: str = "",
    rag_context: str = "",
) -> Task:
    """
    Creates the CrewAI task for Go-To-Market strategy.
    """
    context_section = (
        f"\nEmpirical GTM & Customer Acquisition Benchmarks (from Knowledge Base):\n{rag_context}\n"
        if rag_context
        else ""
    )

    description = f"""
Formulate a focused Go-To-Market (GTM) and customer acquisition strategy for:

Startup Name: {startup_data.get('name', 'Venture')}
Idea: {startup_data.get('idea', '')}
Country/Region: {startup_data.get('country', 'Global')}
Target Customer: {startup_data.get('target_customer', 'Consumers')}
Budget: {startup_data.get('currency', '$')}{startup_data.get('budget', 0):,}
Market Research Context: {market_summary}
Competitive Landscape: {competitor_summary}
Financial Constraints: {finance_summary}
{context_section}

Provide:
1. Target Audience Strategy & Positioning Message
2. Highest-ROI Customer Acquisition Channels (prioritize unscalable/organic early tactics)
3. Direct Social Media & Content Distribution Playbook
4. First Launch Campaign Concept (how to get the first 100 passionate users)
5. Promotional & Referral Growth Loops
6. Customer Retention & Churn Reduction Tactics
7. Business Model / Growth Score (0-100 integer)

Format your output strictly as a valid JSON object matching this structure:
{{
  "business_model_score": 78,
  "target_audience_strategy": "Core messaging and targeting framework",
  "customer_acquisition_channels": [
    {{
      "channel": "Channel Name",
      "expected_cac": "Low / Medium / High",
      "action_plan": "Specific tactical execution"
    }}
  ],
  "social_media_strategy": "Content and community distribution approach",
  "launch_campaign": "Step-by-step initial user onboarding campaign",
  "promotional_ideas": ["viral tactic 1", "referral mechanism 2"],
  "customer_retention_approach": "Retention mechanism and onboarding triggers",
  "initial_growth_milestone": "First 100 paying customers within 60 days",
  "summary": "Concise 2-sentence executive summary of the acquisition and growth plan."
}}
"""
    return Task(
        description=description,
        expected_output="A structured JSON object detailing acquisition channels, launch campaign, viral loops, retention tactics, and growth score.",
        agent=agent,
    )
