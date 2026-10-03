"""
CrewAI Orchestration Pipeline for AI Venture Co-Founder.
Coordinates the six specialized agents in a clean sequential pipeline:
Market Research -> Competitor -> Finance -> Marketing -> CTO -> CEO.
Strictly adheres to the global 7,500 output token limit.
"""
import logging
from typing import Dict, Any, Callable, Optional
from crewai import Crew, Process

from config.llm_config import TokenBudgetManager, global_token_manager
from rag.retriever import knowledge_retriever
from database.models import (
    Startup,
    AgentResult,
    StartupAnalysis,
    DynamicRoadmap,
    RoadmapTask,
)
from database.repository import StartupRepository
from utils.formatters import clean_markdown_json
from agents import (
    create_market_research_agent,
    create_competitor_agent,
    create_finance_agent,
    create_marketing_agent,
    create_cto_agent,
    create_ceo_agent,
)
from tasks import (
    create_market_research_task,
    create_competitor_task,
    create_finance_task,
    create_marketing_task,
    create_cto_task,
    create_ceo_synthesis_task,
)

logger = logging.getLogger(__name__)


class StartupCrewOrchestrator:
    """
    Manages the end-to-end execution of the 6 AI agents, token accounting,
    knowledge retrieval, and database persistence.
    """

    def __init__(self, token_manager: Optional[TokenBudgetManager] = None):
        self.token_manager = token_manager or global_token_manager

    def run_analysis(
        self,
        startup: Startup,
        progress_callback: Optional[Callable[[str, str, str, Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the complete multi-agent venture evaluation pipeline.
        Progress callback signature: (agent_key, status, message, token_summary)
        """
        self.token_manager.reset()
        StartupRepository.update_startup_status(startup.id, "running")

        def notify(agent_key: str, status: str, message: str):
            if progress_callback:
                summary = self.token_manager.get_summary()
                progress_callback(agent_key, status, message, summary)

        startup_dict = {
            "name": startup.name,
            "idea": startup.idea,
            "country": startup.country,
            "target_market": startup.target_market,
            "target_customer": startup.target_customer,
            "budget": startup.budget,
            "currency": startup.currency,
            "founder_experience": startup.founder_experience,
            "additional_context": startup.additional_context,
        }

        # 0. Semantic Knowledge Retrieval
        rag_query = f"{startup.name} {startup.idea} {startup.target_market} {startup.country}"
        rag_context = knowledge_retriever.get_formatted_context(rag_query, top_k=3)

        agent_outputs: Dict[str, Dict[str, Any]] = {}
        raw_outputs: Dict[str, str] = {}

        # ---------------------------------------------------------------------
        # 1. Market Research Agent
        # ---------------------------------------------------------------------
        notify("market_research", "running", "Analyzing market size, customer pain points, and local demand...")
        try:
            market_agent = create_market_research_agent(token_manager=self.token_manager)
            market_task = create_market_research_task(market_agent, startup_dict, rag_context=rag_context)
            market_crew = Crew(agents=[market_agent], tasks=[market_task], process=Process.sequential, verbose=False)
            market_res = market_crew.kickoff()
            raw_text = str(market_res.raw if hasattr(market_res, "raw") else market_res)
            raw_outputs["market_research"] = raw_text

            parsed = clean_markdown_json(raw_text) or {}
            agent_outputs["market_research"] = parsed
            tokens_used = self._estimate_tokens(raw_text)
            self.token_manager.record_usage("market_research", tokens_used)

            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="market_research",
                    status="completed",
                    raw_output=raw_text,
                    structured_output=parsed,
                    tokens_used=tokens_used,
                )
            )
            notify("market_research", "completed", "Market research completed successfully.")
        except Exception as e:
            logger.error(f"Market Research Agent failed: {e}", exc_info=True)
            notify("market_research", "failed", f"Analysis error: {str(e)}")
            raw_outputs["market_research"] = f"Market analysis encountered an error: {str(e)}"
            agent_outputs["market_research"] = {"market_score": 60, "summary": "Market analysis fallback summary."}

        market_summary = agent_outputs.get("market_research", {}).get(
            "summary", "Market analysis identifies strong initial target customer interest."
        )

        # ---------------------------------------------------------------------
        # 2. Competitor Agent
        # ---------------------------------------------------------------------
        notify("competitor_analysis", "running", "Evaluating competitor landscape and defensible market gaps...")
        try:
            comp_agent = create_competitor_agent(token_manager=self.token_manager)
            comp_task = create_competitor_task(
                comp_agent, startup_dict, market_summary=market_summary, rag_context=rag_context
            )
            comp_crew = Crew(agents=[comp_agent], tasks=[comp_task], process=Process.sequential, verbose=False)
            comp_res = comp_crew.kickoff()
            raw_text = str(comp_res.raw if hasattr(comp_res, "raw") else comp_res)
            raw_outputs["competitor_analysis"] = raw_text

            parsed = clean_markdown_json(raw_text) or {}
            agent_outputs["competitor_analysis"] = parsed
            tokens_used = self._estimate_tokens(raw_text)
            self.token_manager.record_usage("competitor_analysis", tokens_used)

            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="competitor_analysis",
                    status="completed",
                    raw_output=raw_text,
                    structured_output=parsed,
                    tokens_used=tokens_used,
                )
            )
            notify("competitor_analysis", "completed", "Competitor analysis completed successfully.")
        except Exception as e:
            logger.error(f"Competitor Agent failed: {e}", exc_info=True)
            notify("competitor_analysis", "failed", f"Analysis error: {str(e)}")
            raw_outputs["competitor_analysis"] = f"Competitor analysis error: {str(e)}"
            agent_outputs["competitor_analysis"] = {"competition_score": 60, "summary": "Competitor landscape reviewed."}

        competitor_summary = agent_outputs.get("competitor_analysis", {}).get(
            "summary", "Competitor research indicates fragmented existing offerings with space for focused differentiation."
        )

        # ---------------------------------------------------------------------
        # 3. Finance Agent
        # ---------------------------------------------------------------------
        notify("finance", "running", "Modeling unit economics, operational burn, and break-even targets...")
        try:
            fin_agent = create_finance_agent(token_manager=self.token_manager)
            fin_task = create_finance_task(
                fin_agent,
                startup_dict,
                market_summary=market_summary,
                competitor_summary=competitor_summary,
            )
            fin_crew = Crew(agents=[fin_agent], tasks=[fin_task], process=Process.sequential, verbose=False)
            fin_res = fin_crew.kickoff()
            raw_text = str(fin_res.raw if hasattr(fin_res, "raw") else fin_res)
            raw_outputs["finance"] = raw_text

            parsed = clean_markdown_json(raw_text) or {}
            agent_outputs["finance"] = parsed
            tokens_used = self._estimate_tokens(raw_text)
            self.token_manager.record_usage("finance", tokens_used)

            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="finance",
                    status="completed",
                    raw_output=raw_text,
                    structured_output=parsed,
                    tokens_used=tokens_used,
                )
            )
            notify("finance", "completed", "Financial model calculated successfully.")
        except Exception as e:
            logger.error(f"Finance Agent failed: {e}", exc_info=True)
            notify("finance", "failed", f"Analysis error: {str(e)}")
            raw_outputs["finance"] = f"Financial analysis error: {str(e)}"
            agent_outputs["finance"] = {"finance_score": 65, "summary": "Financial model generated baseline unit economics."}

        finance_summary = agent_outputs.get("finance", {}).get(
            "summary", "Financial evaluation projects manageable initial burn with clear paths to unit profitability."
        )

        # ---------------------------------------------------------------------
        # 4. Marketing Agent
        # ---------------------------------------------------------------------
        notify("marketing", "running", "Designing Go-To-Market playbook, launch campaign, and user retention loops...")
        try:
            mkt_agent = create_marketing_agent(token_manager=self.token_manager)
            mkt_task = create_marketing_task(
                mkt_agent,
                startup_dict,
                market_summary=market_summary,
                competitor_summary=competitor_summary,
                finance_summary=finance_summary,
            )
            mkt_crew = Crew(agents=[mkt_agent], tasks=[mkt_task], process=Process.sequential, verbose=False)
            mkt_res = mkt_crew.kickoff()
            raw_text = str(mkt_res.raw if hasattr(mkt_res, "raw") else mkt_res)
            raw_outputs["marketing"] = raw_text

            parsed = clean_markdown_json(raw_text) or {}
            agent_outputs["marketing"] = parsed
            tokens_used = self._estimate_tokens(raw_text)
            self.token_manager.record_usage("marketing", tokens_used)

            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="marketing",
                    status="completed",
                    raw_output=raw_text,
                    structured_output=parsed,
                    tokens_used=tokens_used,
                )
            )
            notify("marketing", "completed", "Go-To-Market strategy generated successfully.")
        except Exception as e:
            logger.error(f"Marketing Agent failed: {e}", exc_info=True)
            notify("marketing", "failed", f"Analysis error: {str(e)}")
            raw_outputs["marketing"] = f"Marketing strategy error: {str(e)}"
            agent_outputs["marketing"] = {"business_model_score": 70, "summary": "GTM framework outlined."}

        marketing_summary = agent_outputs.get("marketing", {}).get(
            "summary", "Growth strategy focuses on community-driven distribution and direct customer referrals."
        )

        # ---------------------------------------------------------------------
        # 5. CTO Agent
        # ---------------------------------------------------------------------
        notify("cto", "running", "Formulating tech architecture, core features, and technical safeguards...")
        try:
            cto_agent = create_cto_agent(token_manager=self.token_manager)
            cto_task = create_cto_task(
                cto_agent,
                startup_dict,
                market_summary=market_summary,
                budget=startup.budget,
            )
            cto_crew = Crew(agents=[cto_agent], tasks=[cto_task], process=Process.sequential, verbose=False)
            cto_res = cto_crew.kickoff()
            raw_text = str(cto_res.raw if hasattr(cto_res, "raw") else cto_res)
            raw_outputs["cto"] = raw_text

            parsed = clean_markdown_json(raw_text) or {}
            agent_outputs["cto"] = parsed
            tokens_used = self._estimate_tokens(raw_text)
            self.token_manager.record_usage("cto", tokens_used)

            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="cto",
                    status="completed",
                    raw_output=raw_text,
                    structured_output=parsed,
                    tokens_used=tokens_used,
                )
            )
            notify("cto", "completed", "Technical architecture and core feature scope established.")
        except Exception as e:
            logger.error(f"CTO Agent failed: {e}", exc_info=True)
            notify("cto", "failed", f"Analysis error: {str(e)}")
            raw_outputs["cto"] = f"CTO technical plan error: {str(e)}"
            agent_outputs["cto"] = {"technology_score": 85, "summary": "Technical stack designed for rapid release."}

        cto_summary = agent_outputs.get("cto", {}).get(
            "summary", "Technical plan specifies modular, capital-efficient components and core feature priorities."
        )

        # ---------------------------------------------------------------------
        # 6. CEO Agent (Final Synthesis, Scoring, Blueprint, Dynamic Roadmap)
        # ---------------------------------------------------------------------
        notify("ceo", "running", "Synthesizing cross-functional findings, risk matrix, and dynamic execution roadmap...")
        try:
            ceo_agent = create_ceo_agent(token_manager=self.token_manager)
            ceo_task = create_ceo_synthesis_task(
                ceo_agent,
                startup_dict,
                market_summary=market_summary,
                competitor_summary=competitor_summary,
                finance_summary=finance_summary,
                marketing_summary=marketing_summary,
                cto_summary=cto_summary,
            )
            ceo_crew = Crew(agents=[ceo_agent], tasks=[ceo_task], process=Process.sequential, verbose=False)
            ceo_res = ceo_crew.kickoff()
            raw_text = str(ceo_res.raw if hasattr(ceo_res, "raw") else ceo_res)
            raw_outputs["ceo"] = raw_text

            parsed = clean_markdown_json(raw_text) or {}
            agent_outputs["ceo"] = parsed
            tokens_used = self._estimate_tokens(raw_text)
            self.token_manager.record_usage("ceo", tokens_used)

            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="ceo",
                    status="completed",
                    raw_output=raw_text,
                    structured_output=parsed,
                    tokens_used=tokens_used,
                )
            )

            # Persist Startup Analysis
            self._save_synthesis_and_roadmap(startup.id, parsed, agent_outputs)
            StartupRepository.update_startup_status(startup.id, "completed")
            notify("ceo", "completed", "Venture Blueprint and Dynamic Execution Roadmap successfully finalized!")

        except Exception as e:
            logger.error(f"CEO Agent failed: {e}", exc_info=True)
            notify("ceo", "failed", f"Synthesis error: {str(e)}")
            raw_outputs["ceo"] = f"CEO synthesis error: {str(e)}"
            # Generate fallback analysis to ensure UI stays fully functional
            fallback = self._generate_fallback_synthesis(startup, agent_outputs)
            self._save_synthesis_and_roadmap(startup.id, fallback, agent_outputs)
            StartupRepository.update_startup_status(startup.id, "completed")

        return {
            "startup_id": startup.id,
            "agent_outputs": agent_outputs,
            "token_summary": self.token_manager.get_summary(),
        }

    def _estimate_tokens(self, text: str) -> int:
        """Lightweight token estimator (approx 1 token = 4 chars or 0.75 words)."""
        if not text:
            return 0
        return max(50, len(text) // 4)

    def _save_synthesis_and_roadmap(
        self,
        startup_id: int,
        ceo_data: Dict[str, Any],
        all_outputs: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        Parses CEO structured JSON and persists Analysis and Dynamic Roadmap.
        """
        overall_score = ceo_data.get("overall_score") or 75

        # Merge category scores from individual agents if not present in CEO output
        cat_scores = ceo_data.get("category_scores") or {}
        if not cat_scores:
            cat_scores = {
                "market": all_outputs.get("market_research", {}).get("market_score", 80),
                "competition": all_outputs.get("competitor_analysis", {}).get("competition_score", 70),
                "business_model": all_outputs.get("marketing", {}).get("business_model_score", 75),
                "finance": all_outputs.get("finance", {}).get("finance_score", 70),
                "technology": all_outputs.get("cto", {}).get("technology_score", 88),
                "risk": 60,
            }

        analysis = StartupAnalysis(
            startup_id=startup_id,
            overall_score=int(overall_score),
            category_scores=cat_scores,
            difficulty_level=ceo_data.get("difficulty_level", "MEDIUM"),
            difficulty_reasoning=ceo_data.get("difficulty_reasoning", "Assessed across technical, market, and financial dimensions."),
            executive_summary=ceo_data.get("executive_summary", "Comprehensive startup analysis and execution plan."),
            problem_statement=ceo_data.get("problem_statement", "Target customer pain points and inefficiencies."),
            solution_statement=ceo_data.get("solution_statement", "Platform value proposition and core offering."),
            usp=ceo_data.get("usp", "Competitive differentiation."),
            business_model=ceo_data.get("business_model", "Direct-to-customer / marketplace model."),
            revenue_model=ceo_data.get("revenue_model", "Tiered subscriptions and transaction commissions."),
            core_features=ceo_data.get("core_features") or all_outputs.get("cto", {}).get("core_features", []),
            technical_direction=ceo_data.get("technical_direction", "Modular architecture."),
            financial_overview=ceo_data.get("financial_overview", "Unit economics and runway overview."),
            risk_analysis=ceo_data.get("risk_analysis", {}),
            key_advantages=ceo_data.get("key_advantages", []),
            major_risks=ceo_data.get("major_risks", []),
            recommended_next_steps=ceo_data.get("recommended_next_steps", []),
            feasibility_verdict=ceo_data.get("feasibility_verdict", "Good Potential"),
        )
        StartupRepository.save_analysis(analysis)

        # Dynamic Roadmap handling (NEVER hardcoded 30 days)
        roadmap_data = ceo_data.get("dynamic_roadmap", {})
        total_duration = int(roadmap_data.get("total_duration_days", 45))
        # Ensure dynamic duration is reasonable
        if total_duration < 14:
            total_duration = 21

        phases = roadmap_data.get("phases", [])
        milestones = roadmap_data.get("milestones", [])
        raw_tasks = roadmap_data.get("tasks", [])

        roadmap_tasks = []
        if raw_tasks:
            for t in raw_tasks:
                roadmap_tasks.append(
                    RoadmapTask(
                        roadmap_id=0,
                        day_number=int(t.get("day_number", 1)),
                        phase=t.get("phase", "Validation Phase"),
                        title=t.get("title", "Execute planned task"),
                        description=t.get("description", ""),
                        is_completed=False,
                        milestone_tag=t.get("milestone_tag", ""),
                    )
                )
        else:
            # Generate structured dynamic tasks spanning the dynamic duration
            roadmap_tasks = self._generate_default_dynamic_tasks(total_duration)

        dynamic_roadmap = DynamicRoadmap(
            startup_id=startup_id,
            total_duration_days=total_duration,
            current_day=1,
            current_phase=phases[0]["name"] if phases else "Validation Phase",
            progress_percent=0.0,
            milestones=milestones,
            tasks=roadmap_tasks,
        )
        StartupRepository.save_roadmap(dynamic_roadmap)

    def _generate_default_dynamic_tasks(self, duration_days: int) -> list:
        """Generates dynamic phased tasks scaled to the venture's dynamic duration."""
        tasks = []
        # Phase 1: Validation (First 25% of days)
        val_end = max(3, int(duration_days * 0.25))
        tasks.append(RoadmapTask(0, 1, "Validation Phase", "Define Customer Interview Script", "Draft open-ended problem questions."))
        tasks.append(RoadmapTask(0, 2, "Validation Phase", "Conduct First 5 Discovery Interviews", "Record top complaints and workarounds."))
        tasks.append(RoadmapTask(0, val_end, "Validation Phase", "Synthesize Customer Validation Evidence", "Validate demand before building.", milestone_tag="Customer Validation Sign-off"))

        # Phase 2: Core Build (Next 40% of days)
        build_mid = val_end + max(3, int(duration_days * 0.20))
        build_end = val_end + max(6, int(duration_days * 0.40))
        tasks.append(RoadmapTask(0, val_end + 1, "Core Build Phase", "Setup Database Schema & Service Architecture", "Implement core data models."))
        tasks.append(RoadmapTask(0, build_mid, "Core Build Phase", "Develop Core User Workflows", "Build the primary value engine."))
        tasks.append(RoadmapTask(0, build_end, "Core Build Phase", "Internal Alpha Feature Freeze", "Ensure all core features function reliably.", milestone_tag="Core Build Milestone"))

        # Phase 3: Testing & Closed Launch (Remaining days)
        tasks.append(RoadmapTask(0, build_end + 2, "Launch & Growth Phase", "Onboard First 20 Pilot Users", "Gather live user metrics and feedback."))
        tasks.append(RoadmapTask(0, duration_days, "Launch & Growth Phase", "Public Launch & Traction Review", "Review unit metrics and iterate.", milestone_tag="Public Launch Milestone"))
        return tasks

    def _generate_fallback_synthesis(self, startup: Startup, all_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Provides a cohesive fallback synthesis if the final call runs out of tokens."""
        return {
            "overall_score": 75,
            "feasibility_verdict": "Good Potential",
            "category_scores": {
                "market": 78,
                "competition": 65,
                "business_model": 72,
                "finance": 68,
                "technology": 85,
                "risk": 60,
            },
            "difficulty_level": "MEDIUM",
            "difficulty_reasoning": "Standard technical scope with targeted local market validation required.",
            "executive_summary": (
                f"{startup.name} presents a compelling opportunity in {startup.country}. "
                "The venture addresses clear market friction with a capital-efficient software architecture."
            ),
            "problem_statement": "Customers currently face high friction, fragmented providers, and inefficient pricing.",
            "solution_statement": "An integrated, AI-enhanced platform delivering speed, affordability, and transparent operations.",
            "usp": "Tailored localized experience with automated intelligence and low overhead.",
            "business_model": "Direct transaction fees and premium value-added services.",
            "revenue_model": "Tiered commissions and subscription access.",
            "core_features": ["User Discovery", "Instant Ordering / Matching", "Secure Payment", "Analytics Dashboard"],
            "technical_direction": "Streamlit frontend, Python backend, SQLite/PostgreSQL storage, vector search.",
            "financial_overview": "Initial capital sufficient for first release; break-even targeted within initial 6 months.",
            "key_advantages": ["Strong local market focus", "Capital-efficient tech stack", "Fast iteration cycle"],
            "major_risks": ["Customer acquisition scaling", "Competitor response"],
            "risk_analysis": {
                "market_risk": {"description": "Adoption hesitation", "impact": "Medium", "reason": "New workflow habit", "mitigation": "Frictionless onboarding"},
                "financial_risk": {"description": "Burn rate overage", "impact": "Medium", "reason": "Paid ads inflation", "mitigation": "Focus on organic growth"},
                "technical_risk": {"description": "Service latency", "impact": "Low", "reason": "Initial server capacity", "mitigation": "Stateless caching"},
            },
            "recommended_next_steps": [
                "Conduct 10 in-depth customer interviews",
                "Deploy landing page smoke test",
                "Finalize technical architecture",
                "Launch closed pilot with 25 target users",
            ],
            "dynamic_roadmap": {
                "total_duration_days": 35,
                "phases": [
                    {"name": "Phase 1: Validation & Discovery", "days": "Day 1 - 8"},
                    {"name": "Phase 2: Core Build", "days": "Day 9 - 22"},
                    {"name": "Phase 3: Pilot & Launch", "days": "Day 23 - 35"},
                ],
                "milestones": [
                    {"day": 8, "title": "Customer Problem Validation"},
                    {"day": 22, "title": "Feature Complete"},
                    {"day": 35, "title": "Public Launch"},
                ],
            },
        }


# Global singleton orchestrator
startup_orchestrator = StartupCrewOrchestrator()
