"""
Analysis Service.
Coordinates agent orchestration, result retrieval, and Co-Founder Chat interactions.
"""
from typing import Optional, Dict, Any, Callable, List
from database.models import Startup, StartupAnalysis, AgentResult, ChatMessage
from database.repository import StartupRepository
from crew.startup_crew import startup_orchestrator
from config.llm_config import create_agent_llm
from rag.retriever import knowledge_retriever


class AnalysisService:

    @staticmethod
    def run_full_analysis(
        startup: Startup,
        progress_callback: Optional[Callable[[str, str, str, Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Runs the 6-agent CrewAI orchestration workflow."""
        return startup_orchestrator.run_analysis(startup, progress_callback=progress_callback)

    @staticmethod
    def get_analysis_for_startup(startup_id: int) -> Optional[StartupAnalysis]:
        return StartupRepository.get_analysis(startup_id)

    @staticmethod
    def get_agent_results(startup_id: int) -> Dict[str, AgentResult]:
        return StartupRepository.get_agent_results(startup_id)

    @staticmethod
    def ask_ai_cofounder(startup_id: int, user_question: str) -> str:
        """
        AI Co-Founder chat response using the CEO / Co-Founder context and RAG knowledge.
        Does NOT create an extra 7th agent; uses the centralized CEO reasoning model.
        """
        startup = StartupRepository.get_startup(startup_id)
        if not startup:
            return "Startup context not found. Please select or create a startup first."

        analysis = StartupAnalysis(startup_id=startup_id)
        existing_analysis = StartupRepository.get_analysis(startup_id)
        if existing_analysis:
            analysis = existing_analysis

        rag_context = knowledge_retriever.get_formatted_context(user_question, top_k=2)

        roadmap = StartupRepository.get_roadmap(startup_id)
        roadmap_status = (
            f"Day {roadmap.current_day} of {roadmap.total_duration_days} ({roadmap.current_phase}, {roadmap.progress_percent:.0f}% complete)"
            if roadmap
            else "Roadmap not generated yet"
        )

        prompt = f"""
You are the AI Co-Founder and CEO of '{startup.name}'.
Your founder is asking you a question or seeking strategic guidance.

Startup Context:
- Idea: {startup.idea}
- Country/Market: {startup.country} ({startup.target_market})
- Target Customer: {startup.target_customer}
- Available Budget: {startup.currency}{float(startup.budget or 0):,.0f}
- Feasibility Verdict: {analysis.feasibility_verdict} (Score: {analysis.overall_score}/100)
- Core Business Model: {analysis.business_model}
- Execution Roadmap Status: {roadmap_status}
- Known Risks: {', '.join(analysis.major_risks[:3]) if analysis.major_risks else 'Standard venture risks'}

{rag_context}

Founder Question: "{user_question}"

Respond directly as an insightful, collaborative, and pragmatic virtual co-founder.
Be candid, actionable, concise, and encourage evidence-based execution.
Avoid fluff. Keep the response under 180 words.
"""
        # Save user message
        StartupRepository.save_chat_message(
            ChatMessage(startup_id=startup_id, sender="user", message=user_question)
        )

        try:
            llm = create_agent_llm("ceo")
            response = llm.call(prompt)
            ai_reply = str(response).strip()
        except Exception as e:
            ai_reply = (
                f"As your co-founder, I recommend focusing on customer demand first. "
                f"We should validate this directly with 10 user interviews in {startup.country}."
            )

        # Save AI reply
        StartupRepository.save_chat_message(
            ChatMessage(startup_id=startup_id, sender="ai_cofounder", message=ai_reply)
        )

        return ai_reply

    @staticmethod
    def get_chat_history(startup_id: int) -> List[ChatMessage]:
        return StartupRepository.get_chat_history(startup_id)
