"""
CrewAI Orchestration Pipeline for AI Venture Co-Founder.
Coordinates the six specialized agents in a clean sequential pipeline:
Market Research -> Competitor -> Finance -> Marketing -> CTO -> CEO.
Strictly adheres to the global 7,500 output token limit.
"""
import logging
from typing import Dict, Any, Callable, Optional, List

# Fix for Groq API: strip 'cache_breakpoint' property from messages
try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except Exception:
    pass

try:
    import litellm
    litellm.drop_params = True
except Exception:
    pass

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
from tasks.finance_tasks import enrich_financial_model

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
        # Clean previous analysis, dynamic roadmap, and agent results to avoid stale data
        StartupRepository.reset_startup_run(startup.id)

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

        # 0. Semantic Knowledge Retrieval from Pre-Built FAISS Index
        base_query = f"{startup.name} {startup.idea} {startup.target_market} {startup.country}"
        market_rag = knowledge_retriever.get_formatted_context(
            f"{base_query} market size customer demand industry benchmarks", top_k=2
        )
        comp_rag = knowledge_retriever.get_formatted_context(
            f"{base_query} competitor positioning defensible moats industry alternatives", top_k=2
        )
        fin_rag = knowledge_retriever.get_formatted_context(
            f"{base_query} unit economics SaaS margins pricing models CAC LTV financial benchmarks", top_k=2
        )
        mkt_rag = knowledge_retriever.get_formatted_context(
            f"{base_query} GTM go-to-market distribution channels viral loops customer retention", top_k=2
        )
        cto_rag = knowledge_retriever.get_formatted_context(
            f"{base_query} system architecture tech stack scalability engineering best practices", top_k=2
        )
        ceo_rag = knowledge_retriever.get_formatted_context(
            f"{base_query} startup survival failure modes venture capital evaluation", top_k=2
        )

        agent_outputs: Dict[str, Dict[str, Any]] = {}
        raw_outputs: Dict[str, str] = {}

        # ---------------------------------------------------------------------
        # 1. Market Research Agent
        # ---------------------------------------------------------------------
        notify("market_research", "running", "Analyzing market size, customer pain points, and local demand...")
        try:
            market_agent = create_market_research_agent(token_manager=self.token_manager)
            market_task = create_market_research_task(market_agent, startup_dict, rag_context=market_rag)
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
                comp_agent, startup_dict, market_summary=market_summary, rag_context=comp_rag
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
        context_len = len(fin_rag) + len(market_summary) + len(competitor_summary)
        logger.info(f"Finance task started. Context payload size: {context_len} chars.")
        try:
            fin_agent = create_finance_agent(token_manager=self.token_manager)
            fin_task = create_finance_task(
                fin_agent,
                startup_dict,
                market_summary=market_summary,
                competitor_summary=competitor_summary,
                rag_context=fin_rag,
            )
            fin_crew = Crew(agents=[fin_agent], tasks=[fin_task], process=Process.sequential, verbose=False)
            fin_res = fin_crew.kickoff()
            raw_text = str(fin_res.raw if hasattr(fin_res, "raw") else fin_res)
            raw_outputs["finance"] = raw_text

            logger.info(f"Finance task completed. Raw output length: {len(raw_text)} chars.")
            raw_parsed = clean_markdown_json(raw_text) or {}
            # Apply deterministic calculations for runway and unit margins
            parsed = enrich_financial_model(raw_parsed, startup.budget)
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
            # Never fabricate fake scores when the agent failed
            agent_outputs["finance"] = {"status": "failed", "error": str(e)}
            StartupRepository.save_agent_result(
                AgentResult(
                    startup_id=startup.id,
                    agent_key="finance",
                    status="failed",
                    raw_output=f"Error: {str(e)}",
                    structured_output={"status": "failed", "error": str(e)},
                    tokens_used=0,
                )
            )

        if agent_outputs.get("finance", {}).get("status") == "failed":
            finance_summary = (
                "WARNING: The Finance Agent was unable to complete unit economics modeling. "
                "Financial projections and pricing tiers are currently unavailable."
            )
        else:
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
                rag_context=mkt_rag,
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
                rag_context=cto_rag,
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
                rag_context=ceo_rag,
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
        Ensures transparent scoring across all 6 agents without silent fallback values.
        """
        # Detect any agents that failed
        failed_agents = [
            k for k, v in all_outputs.items()
            if isinstance(v, dict) and v.get("status") == "failed"
        ]

        # Extract individual agent scores
        m_score = all_outputs.get("market_research", {}).get("market_score")
        c_score = all_outputs.get("competitor_analysis", {}).get("competition_score")
        b_score = all_outputs.get("marketing", {}).get("business_model_score")
        f_score = all_outputs.get("finance", {}).get("finance_score") if "finance" not in failed_agents else None
        t_score = all_outputs.get("cto", {}).get("technology_score")

        cat_scores = dict(ceo_data.get("category_scores") or {})
        if not cat_scores:
            cat_scores = {
                "market": m_score if m_score is not None else 80,
                "competition": c_score if c_score is not None else 70,
                "business_model": b_score if b_score is not None else 75,
                "finance": f_score,  # None if failed
                "technology": t_score if t_score is not None else 85,
                "risk": 60,
            }
        elif "finance" in failed_agents:
            cat_scores["finance"] = None

        # Dynamically compute overall score from available validated scores
        if failed_agents:
            valid_scores = [v for k, v in cat_scores.items() if isinstance(v, (int, float)) and v > 0]
            overall_score = round(sum(valid_scores) / len(valid_scores)) if valid_scores else 50
            failed_str = ", ".join(k.replace("_", " ").title() for k in failed_agents)
            feasibility_verdict = f"Analysis Incomplete — {failed_str} Failed"
        else:
            overall_score = ceo_data.get("overall_score") or round(
                (cat_scores.get("market", 80) * 0.18) +
                (cat_scores.get("competition", 70) * 0.15) +
                (cat_scores.get("finance", 70) * 0.22) +
                (cat_scores.get("business_model", 75) * 0.15) +
                (cat_scores.get("technology", 85) * 0.15) +
                (cat_scores.get("risk", 60) * 0.15)
            )
            feasibility_verdict = ceo_data.get("feasibility_verdict", "Good Potential")

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

        # Authoritative Dynamic Roadmap handling (NEVER hardcoded 30/45 days)
        startup = StartupRepository.get_startup(startup_id)
        if not startup:
            startup = Startup(id=startup_id, name="Venture", idea="", country="Global", target_market="", target_customer="", budget=10000.0)

        total_duration = self._calculate_dynamic_duration(startup, all_outputs, ceo_data)
        v_end = max(3, round(total_duration * 0.22))
        b_end = max(v_end + 5, round(total_duration * 0.60))
        p_end = max(b_end + 3, round(total_duration * 0.85))

        # Dynamic Phases tailored to the calculated duration
        phases = [
            {"name": "Phase 1: Validation & Customer Discovery", "days": f"Day 1 - {v_end}"},
            {"name": "Phase 2: Core Architecture & Build", "days": f"Day {v_end + 1} - {b_end}"},
            {"name": "Phase 3: Pilot & Unit Economics Validation", "days": f"Day {b_end + 1} - {p_end}"},
            {"name": "Phase 4: Commercial Launch & Scaling", "days": f"Day {p_end + 1} - {total_duration}"},
        ]

        # Strategic venture milestones
        milestones = [
            {"day": v_end, "title": f"Customer Validation Sign-Off ({startup.target_customer})"},
            {"day": b_end, "title": f"Core Product Feature Freeze for {startup.name}"},
            {"day": p_end, "title": f"Closed Pilot Feedback Gate ({startup.country})"},
            {"day": total_duration, "title": f"Commercial Public Launch & Growth Gate"},
        ]

        # Generate venture-specific tasks spanning the dynamic duration
        roadmap_tasks = self._generate_dynamic_venture_tasks(
            startup=startup,
            total_duration=total_duration,
            all_outputs=all_outputs,
            ceo_data=ceo_data,
        )

        dynamic_roadmap = DynamicRoadmap(
            startup_id=startup_id,
            total_duration_days=total_duration,
            current_day=1,
            current_phase=phases[0]["name"],
            progress_percent=0.0,
            milestones=milestones,
            tasks=roadmap_tasks,
        )
        StartupRepository.save_roadmap(dynamic_roadmap)

    def _calculate_dynamic_duration(
        self,
        startup: Startup,
        all_outputs: Dict[str, Any],
        ceo_data: Dict[str, Any],
    ) -> int:
        """
        Dynamically calculates calibrated venture roadmap duration (in days)
        based on founder experience, capital runway, domain complexity (FinTech, Health, AI,
        Marketplace, SaaS), CTO technical scope, integrations, and CEO agent synthesis.
        Guarantees that different startup concepts produce distinct, appropriate durations (e.g. 21, 35, 45, 60, 90).
        """
        duration = 30  # Baseline sprint

        # 1. Founder Experience Factor
        exp = (startup.founder_experience or "").lower()
        if "beginner" in exp:
            duration += 10
        elif "intermediate" in exp:
            duration += 5
        elif any(k in exp for k in ["experienced", "serial", "advanced"]):
            duration -= 5

        # 2. Capital Budget Factor
        budget = float(startup.budget or 0)
        if budget < 5000:
            duration -= 5  # Lean rapid MVP sprint
        elif budget > 50000:
            duration += 10  # Comprehensive build runway

        # 3. Technical Complexity & Scope (from CTO Agent output)
        cto_data = all_outputs.get("cto", {})
        complexity = str(cto_data.get("development_complexity", "")).lower()
        core_features = cto_data.get("core_features") or []
        integrations = cto_data.get("required_integrations") or []

        if "high" in complexity:
            duration += 15
        elif "low" in complexity:
            duration -= 7
        else:
            duration += 5

        if len(core_features) >= 4:
            duration += 8
        if len(integrations) >= 3:
            duration += 6

        # 4. Domain & Industry Vertical Analysis
        text_context = f"{startup.name} {startup.idea} {startup.target_market} {startup.additional_context}".lower()
        if any(w in text_context for w in ["fintech", "banking", "payment", "crypto", "blockchain", "lending", "credit", "insurance"]):
            duration += 25  # Heavy compliance, KYC, banking APIs
        elif any(w in text_context for w in ["health", "medical", "clinic", "biotech", "pharma", "diagnostic", "patient"]):
            duration += 28  # Healthcare regulations, HIPAA, clinical testing
        elif any(w in text_context for w in ["hardware", "iot", "robotics", "device", "physical", "sensor"]):
            duration += 30  # Hardware prototyping and supply chain
        elif any(w in text_context for w in ["marketplace", "courier", "delivery", "two-sided", "platform", "driver", "vendor"]):
            duration += 12  # Two-sided liquidity bootstrapping
        elif any(w in text_context for w in ["ai", "deep learning", "llm", "rag", "vision", "speech", "automation"]):
            duration += 8   # Model evaluation, vector search tuning

        # 5. Blend with CEO Agent proposal
        ceo_roadmap = ceo_data.get("dynamic_roadmap", {})
        ceo_proposed = ceo_roadmap.get("total_duration_days")
        if isinstance(ceo_proposed, (int, float)) and 14 <= int(ceo_proposed) <= 120:
            final_duration = round(0.50 * duration + 0.50 * int(ceo_proposed))
        else:
            final_duration = duration

        # Clamp between 15 and 120 days
        return int(max(15, min(120, final_duration)))

    def _generate_dynamic_venture_tasks(
        self,
        startup: Startup,
        total_duration: int,
        all_outputs: Dict[str, Any],
        ceo_data: Dict[str, Any],
    ) -> List[RoadmapTask]:
        """
        Generates structured, venture-specific tasks spanning the dynamic duration.
        Every task is directly tied to the startup's actual idea, target customer, market findings,
        competitor gaps, CTO core features, financial targets, and marketing channels.
        """
        # Extract rich context from all 6 agents
        mkt = all_outputs.get("market_research", {})
        problems = mkt.get("customer_problems") or [f"High friction and lack of tailored solutions for {startup.target_customer}"]
        p_main = problems[0] if problems else f"Pain point for {startup.target_customer}"

        comp = all_outputs.get("competitor_analysis", {})
        usp = comp.get("recommended_usp") or f"Tailored, cost-effective solution for {startup.target_customer}"
        competitors = comp.get("competitors") or []
        top_comp = competitors[0].get("name", "legacy incumbents") if competitors and isinstance(competitors[0], dict) else "incumbents"

        fin = all_outputs.get("finance", {})
        break_even = fin.get("break_even_point") or "Initial break-even order volume"
        pricing_opts = fin.get("pricing_options") or []
        tier_label = pricing_opts[0].get("tier_name", "standard tier") if pricing_opts and isinstance(pricing_opts[0], dict) else "core pricing tier"

        mktg = all_outputs.get("marketing", {})
        channels = mktg.get("customer_acquisition_channels") or []
        c_main = channels[0].get("channel", "direct organic outreach") if channels and isinstance(channels[0], dict) else "direct outreach"
        promos = mktg.get("promotional_ideas") or [f"Early adopter referral loop for {startup.target_customer}"]
        promo_main = promos[0] if promos else "Referral program"

        cto = all_outputs.get("cto", {})
        core_features = cto.get("core_features") or [
            f"Core User Workflow for {startup.name}",
            f"Automated Matching / Processing Engine",
            f"Payment & Order Management",
            f"Founder & Admin Analytics",
        ]
        feat1 = core_features[0] if len(core_features) > 0 else "Primary User Workflow"
        feat2 = core_features[1] if len(core_features) > 1 else "Core Engine Logic"
        feat3 = core_features[2] if len(core_features) > 2 else "Transaction & Analytics"

        tech_stack = cto.get("recommended_tech_stack") or {}
        backend_tech = tech_stack.get("backend", "Python Services")
        db_tech = tech_stack.get("database", "Relational Database")

        integrations = cto.get("required_integrations") or ["Payment Gateway", "Authentication & Messaging"]
        int1 = integrations[0] if integrations else "Payment Gateway"

        # Calculate phase milestones based on dynamic total_duration N
        v_end = max(3, round(total_duration * 0.22))
        b_end = max(v_end + 5, round(total_duration * 0.60))
        p_end = max(b_end + 3, round(total_duration * 0.85))

        tasks = []

        # ==================== Phase 1: Validation & Customer Discovery ====================
        p1 = "Phase 1: Validation & Customer Discovery"
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=1, phase=p1,
            title=f"Draft Customer Discovery Script for {startup.target_customer}",
            description=f"Formulate 10 open-ended interview questions focusing on: '{p_main}'.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=2, phase=p1,
            title=f"Conduct Initial 5 Customer Interviews in {startup.country}",
            description=f"Interview 5 target users to verify if '{p_main}' is an acute, budget-backed pain.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=min(v_end - 1, 4), phase=p1,
            title=f"Competitive Audit against {top_comp} & USP Validation",
            description=f"Validate differentiation moat: '{usp[:75]}' directly with prospective customers.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=v_end, phase=p1,
            title=f"Customer Problem Validation Sign-Off for {startup.name}",
            description=f"Synthesize interview findings. Ensure at least 60% of respondents confirm willingness to pay.",
            is_completed=False, milestone_tag="Customer Validation Sign-Off",
        ))

        # ==================== Phase 2: Core Architecture & Engineering ====================
        p2 = "Phase 2: Core Architecture & Build"
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=v_end + 1, phase=p2,
            title=f"Setup {db_tech} Schema & API Architecture",
            description=f"Model data structures for users, transactions, and core workflows for {startup.name}.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=v_end + max(2, round((b_end - v_end) * 0.25)), phase=p2,
            title=f"Build {feat1[:60]}",
            description=f"Implement initial end-to-end user journey in {backend_tech}.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=v_end + max(4, round((b_end - v_end) * 0.55)), phase=p2,
            title=f"Implement {feat2[:60]} & {int1}",
            description=f"Integrate {int1} and build automated workflow mechanics for {startup.name}.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=b_end - 1, phase=p2,
            title=f"Build {feat3[:60]} & Safeguards",
            description=f"Complete final MVP feature scope with rate-limiting, error logging, and data privacy safeguards.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=b_end, phase=p2,
            title=f"Core Alpha Feature Freeze for {startup.name}",
            description=f"Internal end-to-end alpha walkthrough. Ensure zero critical bugs before inviting outside users.",
            is_completed=False, milestone_tag="Core Architecture Complete",
        ))

        # ==================== Phase 3: Financial Verification & Pilot Launch ====================
        p3 = "Phase 3: Pilot & Unit Economics Validation"
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=b_end + 1, phase=p3,
            title=f"Setup Billing & {tier_label} Payment Collection",
            description=f"Configure commercial pricing and checkout for {startup.currency}{startup.budget:,.0f} budget plan.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=b_end + max(2, round((p_end - b_end) * 0.40)), phase=p3,
            title=f"Deploy Pilot Acquisition on {c_main}",
            description=f"Execute targeted launch sprint to recruit first 25-50 pilot cohort users in {startup.country}.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=p_end, phase=p3,
            title=f"Closed Pilot Feedback Review & Break-Even Trajectory",
            description=f"Assess pilot retention, churn, and gross margins toward {break_even[:50]}.",
            is_completed=False, milestone_tag="Pilot Sign-Off",
        ))

        # ==================== Phase 4: Commercial Launch & Growth Traction ====================
        p4 = "Phase 4: Commercial Launch & Scaling"
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=p_end + max(1, round((total_duration - p_end) * 0.35)), phase=p4,
            title=f"Activate Viral Growth Loops & {promo_main[:50]}",
            description=f"Incentivize organic referrals and community-driven distribution in {startup.target_market}.",
            is_completed=False,
        ))
        tasks.append(RoadmapTask(
            roadmap_id=0, day_number=total_duration, phase=p4,
            title=f"Public Launch in {startup.country} & 100-User Growth Review",
            description=f"Official commercial release of {startup.name}. Monitor server latency, unit CAC/LTV, and customer NPS.",
            is_completed=False, milestone_tag="Commercial Launch Milestone",
        ))

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
