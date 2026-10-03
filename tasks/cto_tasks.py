"""
Technical Planning & CTO Task definition for CrewAI.
"""
from typing import Dict, Any
from crewai import Task, Agent


def create_cto_task(
    agent: Agent,
    startup_data: Dict[str, Any],
    market_summary: str = "",
    budget: float = 0.0,
    rag_context: str = "",
) -> Task:
    """
    Creates the CrewAI task for technical architecture and software planning.
    """
    context_section = (
        f"\nEmpirical Technical Architecture & Engineering Standards (from Knowledge Base):\n{rag_context}\n"
        if rag_context
        else ""
    )

    description = f"""
Architect the software systems, core feature scope, and technology roadmap for:

Startup Name: {startup_data.get('name', 'Venture')}
Idea: {startup_data.get('idea', '')}
Available Capital: {startup_data.get('currency', '$')}{budget:,}
Founder Experience: {startup_data.get('founder_experience', 'Beginner')}
Market Context: {market_summary}
{context_section}

Architect:
1. Recommended Technology Stack (Frontend, Backend, Database, AI Components, Infrastructure)
2. High-level System Architecture
3. Specific AI / Machine Learning Components (RAG, LLM inference, embedding pipelines)
4. Database Requirements & Data Modeling
5. Essential Core Product Features required for the initial launch (prioritized for rapid user validation)
6. Phased Development Roadmap (Sprint allocations, engineering milestones)
7. Required Third-Party Integrations & APIs (payment gateways, notifications, authentication)
8. Technical Risks & Vulnerabilities (latency, security, vendor lock-in) with Mitigations
9. Scalability & Security Safeguards (data encryption, rate limiting, stateless architecture)
10. Development Complexity & Technology Score (0-100 integer)

Format your output strictly as a valid JSON object matching this structure:
{{
  "technology_score": 91,
  "development_complexity": "Moderate / High / Low",
  "recommended_tech_stack": {{
    "frontend": "Modern responsive interface",
    "backend": "Python / Fast microservices",
    "database": "Relational SQLite / PostgreSQL for scale",
    "ai_layer": "CrewAI orchestration + Vector Search",
    "hosting": "Streamlit Cloud / Containerized Cloud"
  }},
  "system_architecture": "Decoupled service architecture with cached vector retrieval",
  "ai_components": ["Component 1", "Component 2"],
  "database_requirements": "Relational schema for users, orders, and event analytics",
  "core_features": [
    "Feature 1: Core User Workflow",
    "Feature 2: Real-time Discovery Engine",
    "Feature 3: Transaction & Order Processing",
    "Feature 4: Interactive Founder Dashboard"
  ],
  "development_phases": ["Phase 1: Core Architecture", "Phase 2: Alpha Testing", "Phase 3: Production Hardening"],
  "required_integrations": ["Stripe / Local Payment Gateway", "Twilio / SMS Alerts", "Vector DB"],
  "technical_risks": [
    {{
      "risk": "Risk description",
      "severity": "High / Medium / Low",
      "mitigation": "Engineering mitigation strategy"
    }}
  ],
  "scalability_considerations": "Stateless backend with Redis caching and connection pooling",
  "security_considerations": "Strict environment secrets isolation, CSRF protection, and AES encryption",
  "summary": "Concise 2-sentence executive summary of the technology plan and feasibility."
}}
"""
    return Task(
        description=description,
        expected_output="A structured JSON object detailing technology stack, core product features, architecture, technical risks, and tech score.",
        agent=agent,
    )
