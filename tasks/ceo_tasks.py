"""
CEO Executive Synthesis & Decision Task definition for CrewAI.
Combines cross-functional outputs into an authoritative Startup Blueprint,
objective scores, risk matrix, difficulty rating, and dynamic execution roadmap.
"""
from typing import Dict, Any
from crewai import Task, Agent


def create_ceo_synthesis_task(
    agent: Agent,
    startup_data: Dict[str, Any],
    market_summary: str,
    competitor_summary: str,
    finance_summary: str,
    marketing_summary: str,
    cto_summary: str,
    rag_context: str = "",
) -> Task:
    """
    Creates the CrewAI task for final CEO synthesis and startup blueprint generation.
    """
    context_section = (
        f"\nEmpirical Startup Survival & Venture Risk Benchmarks (from Knowledge Base):\n{rag_context}\n"
        if rag_context
        else ""
    )

    description = f"""
As the Lead Co-Founder and CEO, evaluate all specialist intelligence and deliver
the definitive venture assessment, scoring, multi-dimensional risk matrix, and a DYNAMIC EXECUTION ROADMAP.

Startup Information:
- Name: {startup_data.get('name', 'Venture')}
- Core Idea: {startup_data.get('idea', '')}
- Country: {startup_data.get('country', 'Global')}
- Target Market: {startup_data.get('target_market', 'General')}
- Target Customer: {startup_data.get('target_customer', 'Target Users')}
- Available Budget: {startup_data.get('currency', '$')}{startup_data.get('budget', 0):,}
- Founder Experience: {startup_data.get('founder_experience', 'Beginner')}
- Additional Context: {startup_data.get('additional_context', 'None')}

Executive Summaries from Specialists:
1. Market Research: {market_summary}
2. Competitor Intelligence: {competitor_summary}
3. Financial Unit Economics: {finance_summary}
4. Growth & Go-To-Market: {marketing_summary}
5. CTO Technical Architecture: {cto_summary}
{context_section}
CRITICAL ROADMAP REQUIREMENT:
The execution roadmap MUST NOT have a fixed duration.
DO NOT hardcode a 30-day roadmap.
Dynamically calculate an appropriate total duration in days (e.g., 15, 21, 30, 45, 60, 90, or 120 days)
based on the startup's engineering complexity, regulatory/market validation hurdles, founder experience,
and budget constraints. A simpler consumer service might take 21-30 days to validate, whereas a complex
enterprise B2B or hardware/fintech solution might require 60, 90, or 120 days.

Deliver:
1. Executive Summary & Opportunity Overview
2. Problem Statement & Solution Formulation
3. Core Product Features (first release scope)
4. Defensible Unique Selling Proposition (USP)
5. Business Model & Revenue Mechanics
6. Technical Direction & Financial Overview
7. Difficulty Level (LOW, MEDIUM, HIGH) with specific justification
8. Overall Startup Score (0-100) and Category Scores (Market, Competition, Business Model, Finance, Technology, Risk)
9. Holistic Risk Analysis across 8 dimensions (Market, Customer, Competition, Financial, Technical, Operational, Security/Privacy, Scalability)
10. Dynamic Execution Roadmap with tailored total duration, phases, day-by-day tasks, and key milestones
11. Strategic Recommendation / Feasibility Verdict ("High Potential", "Good Potential", "Pivot & Validate", "High Risk")
12. Recommended Immediate Next Steps

Format your output strictly as a valid JSON object matching this structure:
{{
  "overall_score": 76,
  "feasibility_verdict": "Good Potential",
  "category_scores": {{
    "market": 82,
    "competition": 64,
    "business_model": 73,
    "finance": 68,
    "technology": 91,
    "risk": 59
  }},
  "difficulty_level": "MEDIUM",
  "difficulty_reasoning": "Reasoning analyzing tech scope, market friction, capital requirements, and operational hurdles.",
  "executive_summary": "Comprehensive 3-paragraph executive summary synthesizing the opportunity, economics, and technical path.",
  "problem_statement": "Concise definition of the acute customer problem.",
  "solution_statement": "Articulated value proposition and product solution.",
  "usp": "Core competitive differentiator and defensibility moat.",
  "business_model": "Summary of operating model and customer relationship.",
  "revenue_model": "Revenue streams, pricing mechanics, and margins.",
  "core_features": [
    "Feature 1: User Onboarding & Profile Setup",
    "Feature 2: Real-time Discovery & Matching",
    "Feature 3: Transaction & Payment Engine",
    "Feature 4: Tracking & Analytics Dashboard"
  ],
  "technical_direction": "Architectural direction, key tools, and engineering milestones.",
  "financial_overview": "Capital runway, unit margins, and break-even trajectory.",
  "key_advantages": [
    "Advantage 1: Strong localized market positioning",
    "Advantage 2: Capital-efficient software architecture",
    "Advantage 3: Organic referral loops"
  ],
  "major_risks": [
    "Major Risk 1: Customer acquisition cost inflation",
    "Major Risk 2: Regulatory or operational fulfillment friction"
  ],
  "risk_analysis": {{
    "market_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "customer_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "competition_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "financial_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "technical_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "operational_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "security_privacy_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }},
    "scalability_risk": {{
      "description": "Risk description",
      "impact": "High / Medium / Low",
      "reason": "Why this risk exists",
      "mitigation": "Tactical mitigation strategy"
    }}
  }},
  "recommended_next_steps": [
    "Step 1: Conduct 15 user validation interviews",
    "Step 2: Build clickable interactive prototype",
    "Step 3: Secure initial merchant/supplier LOIs",
    "Step 4: Launch closed alpha with 50 pilot users"
  ],
  "dynamic_roadmap": {{
    "total_duration_days": 45,
    "phases": [
      {{"name": "Phase 1: Validation & Customer Discovery", "days": "Day 1 - 10"}},
      {{"name": "Phase 2: Core Product Architecture & Build", "days": "Day 11 - 25"}},
      {{"name": "Phase 3: Alpha Testing & Iteration", "days": "Day 26 - 35"}},
      {{"name": "Phase 4: Public Launch & Traction", "days": "Day 36 - 45"}}
    ],
    "milestones": [
      {{"day": 10, "title": "Customer Problem Validation"}},
      {{"day": 25, "title": "Core Product Feature Complete"}},
      {{"day": 35, "title": "Closed Alpha Feedback Sign-off"}},
      {{"day": 45, "title": "Public Launch & First 50 Paying Users"}}
    ],
    "tasks": [
      {{
        "day_number": 1,
        "phase": "Phase 1: Validation & Customer Discovery",
        "title": "Define customer interview script & target personas",
        "description": "Draft open-ended questions focusing on pain severity and existing workarounds.",
        "milestone_tag": ""
      }},
      {{
        "day_number": 2,
        "phase": "Phase 1: Validation & Customer Discovery",
        "title": "Launch landing page smoke test for early signups",
        "description": "Collect email pre-registrations to test headline messaging.",
        "milestone_tag": ""
      }},
      {{
        "day_number": 3,
        "phase": "Phase 1: Validation & Customer Discovery",
        "title": "Conduct first 5 customer discovery interviews",
        "description": "Identify key recurring complaints and budget willingness.",
        "milestone_tag": ""
      }},
      {{
        "day_number": 4,
        "phase": "Phase 1: Validation & Customer Discovery",
        "title": "Competitive pricing audit & benchmark testing",
        "description": "Compare unit economics against local alternatives.",
        "milestone_tag": ""
      }},
      {{
        "day_number": 5,
        "phase": "Phase 1: Validation & Customer Discovery",
        "title": "Synthesize customer interview insights into feature backlog",
        "description": "Eliminate low-priority features and freeze first build scope.",
        "milestone_tag": "Validation Milestone"
      }}
    ]
  }}
}}
"""
    return Task(
        description=description,
        expected_output="A structured JSON object with complete Startup Blueprint, scores, risk matrix, difficulty rating, and dynamic execution roadmap.",
        agent=agent,
    )
