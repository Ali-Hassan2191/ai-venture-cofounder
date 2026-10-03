"""
Repository layer for database operations.
Keeps SQL queries completely isolated from UI and business logic.
"""
import json
import sqlite3
from typing import List, Optional, Dict, Any
from database.database import get_db
from database.models import (
    Startup,
    AgentResult,
    StartupAnalysis,
    DynamicRoadmap,
    RoadmapTask,
    ChatMessage,
    ReportMeta,
)


class StartupRepository:

    @staticmethod
    def create_startup(startup: Startup) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO startups (
                    name, idea, country, target_market, target_customer,
                    budget, currency, founder_name, founder_experience, additional_context, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    startup.name,
                    startup.idea,
                    startup.country,
                    startup.target_market,
                    startup.target_customer,
                    startup.budget,
                    startup.currency,
                    startup.founder_name,
                    startup.founder_experience,
                    startup.additional_context,
                    startup.status,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_startup(startup_id: int) -> Optional[Startup]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM startups WHERE id = ?", (startup_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Startup(
                id=row["id"],
                name=row["name"],
                idea=row["idea"],
                country=row["country"],
                target_market=row["target_market"],
                target_customer=row["target_customer"],
                budget=row["budget"],
                currency=row["currency"],
                founder_name=row["founder_name"],
                founder_experience=row["founder_experience"],
                additional_context=row["additional_context"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    @staticmethod
    def get_latest_startup() -> Optional[Startup]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM startups ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return None
            return Startup(
                id=row["id"],
                name=row["name"],
                idea=row["idea"],
                country=row["country"],
                target_market=row["target_market"],
                target_customer=row["target_customer"],
                budget=row["budget"],
                currency=row["currency"],
                founder_name=row["founder_name"],
                founder_experience=row["founder_experience"],
                additional_context=row["additional_context"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    @staticmethod
    def list_startups() -> List[Startup]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM startups ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                Startup(
                    id=r["id"],
                    name=r["name"],
                    idea=r["idea"],
                    country=r["country"],
                    target_market=r["target_market"],
                    target_customer=r["target_customer"],
                    budget=r["budget"],
                    currency=r["currency"],
                    founder_name=r["founder_name"],
                    founder_experience=r["founder_experience"],
                    additional_context=r["additional_context"],
                    status=r["status"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
                for r in rows
            ]

    @staticmethod
    def update_startup_status(startup_id: int, status: str) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE startups SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, startup_id),
            )

    @staticmethod
    def reset_startup_run(startup_id: int) -> None:
        """
        Clears previous run analysis, dynamic roadmap, and agent results for this startup,
        preventing stale or previous run scores from being displayed during/after a new run.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analyses WHERE startup_id = ?", (startup_id,))
            cursor.execute(
                "DELETE FROM roadmap_tasks WHERE roadmap_id IN (SELECT id FROM roadmaps WHERE startup_id = ?)",
                (startup_id,),
            )
            cursor.execute("DELETE FROM roadmaps WHERE startup_id = ?", (startup_id,))
            cursor.execute("DELETE FROM agent_results WHERE startup_id = ?", (startup_id,))
            cursor.execute(
                "UPDATE startups SET status = 'running', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (startup_id,),
            )

    @staticmethod
    def save_agent_result(result: AgentResult) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            # Upsert behavior based on startup_id and agent_key
            cursor.execute(
                "SELECT id FROM agent_results WHERE startup_id = ? AND agent_key = ?",
                (result.startup_id, result.agent_key),
            )
            existing = cursor.fetchone()
            struct_json = json.dumps(result.structured_output or {})

            if existing:
                cursor.execute(
                    """
                    UPDATE agent_results
                    SET status = ?, raw_output = ?, structured_output = ?, tokens_used = ?
                    WHERE id = ?
                    """,
                    (result.status, result.raw_output, struct_json, result.tokens_used, existing["id"]),
                )
                return existing["id"]
            else:
                cursor.execute(
                    """
                    INSERT INTO agent_results (startup_id, agent_key, status, raw_output, structured_output, tokens_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (result.startup_id, result.agent_key, result.status, result.raw_output, struct_json, result.tokens_used),
                )
                return cursor.lastrowid

    @staticmethod
    def get_agent_results(startup_id: int) -> Dict[str, AgentResult]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_results WHERE startup_id = ?", (startup_id,))
            rows = cursor.fetchall()
            results = {}
            for r in rows:
                try:
                    s_output = json.loads(r["structured_output"] or "{}")
                except Exception:
                    s_output = {}
                results[r["agent_key"]] = AgentResult(
                    id=r["id"],
                    startup_id=r["startup_id"],
                    agent_key=r["agent_key"],
                    status=r["status"],
                    raw_output=r["raw_output"],
                    structured_output=s_output,
                    tokens_used=r["tokens_used"],
                    created_at=r["created_at"],
                )
            return results

    @staticmethod
    def save_analysis(analysis: StartupAnalysis) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM analyses WHERE startup_id = ?", (analysis.startup_id,))
            existing = cursor.fetchone()

            cat_json = json.dumps(analysis.category_scores or {})
            feat_json = json.dumps(analysis.core_features or [])
            risk_json = json.dumps(analysis.risk_analysis or {})
            adv_json = json.dumps(analysis.key_advantages or [])
            m_risks_json = json.dumps(analysis.major_risks or [])
            steps_json = json.dumps(analysis.recommended_next_steps or [])

            if existing:
                cursor.execute(
                    """
                    UPDATE analyses
                    SET overall_score = ?, category_scores = ?, difficulty_level = ?, difficulty_reasoning = ?,
                        executive_summary = ?, problem_statement = ?, solution_statement = ?, usp = ?,
                        business_model = ?, revenue_model = ?, core_features = ?, technical_direction = ?,
                        financial_overview = ?, risk_analysis = ?, key_advantages = ?, major_risks = ?,
                        recommended_next_steps = ?, feasibility_verdict = ?
                    WHERE id = ?
                    """,
                    (
                        analysis.overall_score,
                        cat_json,
                        analysis.difficulty_level,
                        analysis.difficulty_reasoning,
                        analysis.executive_summary,
                        analysis.problem_statement,
                        analysis.solution_statement,
                        analysis.usp,
                        analysis.business_model,
                        analysis.revenue_model,
                        feat_json,
                        analysis.technical_direction,
                        analysis.financial_overview,
                        risk_json,
                        adv_json,
                        m_risks_json,
                        steps_json,
                        analysis.feasibility_verdict,
                        existing["id"],
                    ),
                )
                return existing["id"]
            else:
                cursor.execute(
                    """
                    INSERT INTO analyses (
                        startup_id, overall_score, category_scores, difficulty_level, difficulty_reasoning,
                        executive_summary, problem_statement, solution_statement, usp, business_model,
                        revenue_model, core_features, technical_direction, financial_overview, risk_analysis,
                        key_advantages, major_risks, recommended_next_steps, feasibility_verdict
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analysis.startup_id,
                        analysis.overall_score,
                        cat_json,
                        analysis.difficulty_level,
                        analysis.difficulty_reasoning,
                        analysis.executive_summary,
                        analysis.problem_statement,
                        analysis.solution_statement,
                        analysis.usp,
                        analysis.business_model,
                        analysis.revenue_model,
                        feat_json,
                        analysis.technical_direction,
                        analysis.financial_overview,
                        risk_json,
                        adv_json,
                        m_risks_json,
                        steps_json,
                        analysis.feasibility_verdict,
                    ),
                )
                return cursor.lastrowid

    @staticmethod
    def get_analysis(startup_id: int) -> Optional[StartupAnalysis]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analyses WHERE startup_id = ?", (startup_id,))
            row = cursor.fetchone()
            if not row:
                return None

            def safe_json(val, default):
                try:
                    return json.loads(val) if val else default
                except Exception:
                    return default

            return StartupAnalysis(
                id=row["id"],
                startup_id=row["startup_id"],
                overall_score=row["overall_score"],
                category_scores=safe_json(row["category_scores"], {}),
                difficulty_level=row["difficulty_level"],
                difficulty_reasoning=row["difficulty_reasoning"],
                executive_summary=row["executive_summary"],
                problem_statement=row["problem_statement"],
                solution_statement=row["solution_statement"],
                usp=row["usp"],
                business_model=row["business_model"],
                revenue_model=row["revenue_model"],
                core_features=safe_json(row["core_features"], []),
                technical_direction=row["technical_direction"],
                financial_overview=row["financial_overview"],
                risk_analysis=safe_json(row["risk_analysis"], {}),
                key_advantages=safe_json(row["key_advantages"], []),
                major_risks=safe_json(row["major_risks"], []),
                recommended_next_steps=safe_json(row["recommended_next_steps"], []),
                feasibility_verdict=row["feasibility_verdict"],
                created_at=row["created_at"],
            )

    @staticmethod
    def save_roadmap(roadmap: DynamicRoadmap) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM roadmaps WHERE startup_id = ?", (roadmap.startup_id,))
            existing = cursor.fetchone()
            milestones_json = json.dumps(roadmap.milestones or [])

            if existing:
                roadmap_id = existing["id"]
                cursor.execute(
                    """
                    UPDATE roadmaps
                    SET total_duration_days = ?, current_day = ?, current_phase = ?,
                        progress_percent = ?, milestones = ?
                    WHERE id = ?
                    """,
                    (
                        roadmap.total_duration_days,
                        roadmap.current_day,
                        roadmap.current_phase,
                        roadmap.progress_percent,
                        milestones_json,
                        roadmap_id,
                    ),
                )
                # clear old tasks
                cursor.execute("DELETE FROM roadmap_tasks WHERE roadmap_id = ?", (roadmap_id,))
            else:
                cursor.execute(
                    """
                    INSERT INTO roadmaps (startup_id, total_duration_days, current_day, current_phase, progress_percent, milestones)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        roadmap.startup_id,
                        roadmap.total_duration_days,
                        roadmap.current_day,
                        roadmap.current_phase,
                        roadmap.progress_percent,
                        milestones_json,
                    ),
                )
                roadmap_id = cursor.lastrowid

            # Insert tasks
            for task in roadmap.tasks:
                cursor.execute(
                    """
                    INSERT INTO roadmap_tasks (roadmap_id, day_number, phase, title, description, is_completed, notes, milestone_tag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        roadmap_id,
                        task.day_number,
                        task.phase,
                        task.title,
                        task.description,
                        1 if task.is_completed else 0,
                        task.notes,
                        task.milestone_tag,
                    ),
                )
            return roadmap_id

    @staticmethod
    def get_roadmap(startup_id: int) -> Optional[DynamicRoadmap]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roadmaps WHERE startup_id = ?", (startup_id,))
            row = cursor.fetchone()
            if not row:
                return None

            roadmap_id = row["id"]
            cursor.execute("SELECT * FROM roadmap_tasks WHERE roadmap_id = ? ORDER BY day_number ASC, id ASC", (roadmap_id,))
            task_rows = cursor.fetchall()

            tasks = [
                RoadmapTask(
                    id=tr["id"],
                    roadmap_id=tr["roadmap_id"],
                    day_number=tr["day_number"],
                    phase=tr["phase"],
                    title=tr["title"],
                    description=tr["description"],
                    is_completed=bool(tr["is_completed"]),
                    notes=tr["notes"],
                    milestone_tag=tr["milestone_tag"],
                )
                for tr in task_rows
            ]

            try:
                milestones = json.loads(row["milestones"] or "[]")
            except Exception:
                milestones = []

            return DynamicRoadmap(
                id=roadmap_id,
                startup_id=row["startup_id"],
                total_duration_days=row["total_duration_days"],
                current_day=row["current_day"],
                current_phase=row["current_phase"],
                progress_percent=row["progress_percent"],
                milestones=milestones,
                tasks=tasks,
                created_at=row["created_at"],
            )

    @staticmethod
    def toggle_task_completion(task_id: int, is_completed: bool, notes: str = "") -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE roadmap_tasks SET is_completed = ?, notes = ? WHERE id = ?",
                (1 if is_completed else 0, notes, task_id),
            )
            # Recompute roadmap progress
            cursor.execute("SELECT roadmap_id FROM roadmap_tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                r_id = row["roadmap_id"]
                cursor.execute("SELECT COUNT(*) as total, SUM(is_completed) as done FROM roadmap_tasks WHERE roadmap_id = ?", (r_id,))
                stats = cursor.fetchone()
                total = stats["total"] or 1
                done = stats["done"] or 0
                pct = round((done / total) * 100.0, 1)
                cursor.execute("UPDATE roadmaps SET progress_percent = ? WHERE id = ?", (pct, r_id))

    @staticmethod
    def update_roadmap_progress(
        roadmap_id: int,
        current_day: int,
        current_phase: Optional[str] = None,
        progress_percent: Optional[float] = None,
    ) -> None:
        """
        Updates the current day, phase, and progress percentage for a roadmap.
        Authoritative SQLite persistence.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_duration_days, current_day, current_phase, progress_percent FROM roadmaps WHERE id = ?",
                (roadmap_id,),
            )
            rm_row = cursor.fetchone()
            if not rm_row:
                return

            tot_days = rm_row["total_duration_days"] or 30
            clamped_day = max(1, min(tot_days, current_day))

            # Auto-infer phase if not provided
            if not current_phase:
                cursor.execute(
                    "SELECT phase FROM roadmap_tasks WHERE roadmap_id = ? AND day_number <= ? ORDER BY day_number DESC, id DESC LIMIT 1",
                    (roadmap_id, clamped_day),
                )
                p_row = cursor.fetchone()
                if p_row and p_row["phase"]:
                    current_phase = p_row["phase"]
                else:
                    current_phase = rm_row["current_phase"] or "Validation Phase"

            # Auto-calculate progress_percent if not provided
            if progress_percent is None:
                cursor.execute(
                    "SELECT COUNT(*) as total, SUM(is_completed) as done FROM roadmap_tasks WHERE roadmap_id = ?",
                    (roadmap_id,),
                )
                stats = cursor.fetchone()
                total = (stats["total"] if stats else 0) or 0
                done = (stats["done"] if stats else 0) or 0
                if total > 0:
                    progress_percent = round((done / total) * 100.0, 1)
                else:
                    progress_percent = round(min(100.0, (clamped_day / tot_days) * 100.0), 1)

            cursor.execute(
                """
                UPDATE roadmaps
                SET current_day = ?,
                    current_phase = ?,
                    progress_percent = ?
                WHERE id = ?
                """,
                (clamped_day, current_phase, progress_percent, roadmap_id),
            )

    @staticmethod
    def complete_day_tasks(roadmap_id: int, day_number: int) -> None:
        """
        Marks all tasks for a specific day as completed in SQLite and recomputes roadmap progress.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE roadmap_tasks SET is_completed = 1 WHERE roadmap_id = ? AND day_number = ?",
                (roadmap_id, day_number),
            )
            cursor.execute(
                "SELECT COUNT(*) as total, SUM(is_completed) as done FROM roadmap_tasks WHERE roadmap_id = ?",
                (roadmap_id,),
            )
            stats = cursor.fetchone()
            total = (stats["total"] if stats else 0) or 1
            done = (stats["done"] if stats else 0) or 0
            pct = round((done / total) * 100.0, 1)
            cursor.execute("UPDATE roadmaps SET progress_percent = ? WHERE id = ?", (pct, roadmap_id))

    @staticmethod
    def save_chat_message(msg: ChatMessage) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_messages (startup_id, sender, message) VALUES (?, ?, ?)",
                (msg.startup_id, msg.sender, msg.message),
            )
            return cursor.lastrowid

    @staticmethod
    def get_chat_history(startup_id: int) -> List[ChatMessage]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_messages WHERE startup_id = ? ORDER BY timestamp ASC, id ASC", (startup_id,))
            rows = cursor.fetchall()
            return [
                ChatMessage(
                    id=r["id"],
                    startup_id=r["startup_id"],
                    sender=r["sender"],
                    message=r["message"],
                    timestamp=r["timestamp"],
                )
                for r in rows
            ]

    @staticmethod
    def save_report_meta(meta: ReportMeta) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reports (startup_id, file_path, report_title) VALUES (?, ?, ?)",
                (meta.startup_id, meta.file_path, meta.report_title),
            )
            return cursor.lastrowid

    @staticmethod
    def get_reports_for_startup(startup_id: int) -> List[ReportMeta]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE startup_id = ? ORDER BY generated_at DESC", (startup_id,))
            rows = cursor.fetchall()
            return [
                ReportMeta(
                    id=r["id"],
                    startup_id=r["startup_id"],
                    file_path=r["file_path"],
                    report_title=r["report_title"],
                    generated_at=r["generated_at"],
                )
                for r in rows
            ]
