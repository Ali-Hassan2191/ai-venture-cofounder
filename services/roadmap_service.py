"""
Roadmap Service.
Manages the dynamic execution roadmap, progress recalculation, and milestone tracking.
Strictly ensures roadmap durations are dynamic (not fixed 30 days).
"""
from typing import Optional, List, Dict, Any
from database.models import DynamicRoadmap, RoadmapTask
from database.repository import StartupRepository


class RoadmapService:

    @staticmethod
    def get_roadmap_for_startup(startup_id: int) -> Optional[DynamicRoadmap]:
        return StartupRepository.get_roadmap(startup_id)

    @staticmethod
    def toggle_task(task_id: int, is_completed: bool, notes: str = "") -> None:
        StartupRepository.toggle_task_completion(task_id, is_completed, notes=notes)

    @staticmethod
    def advance_day(startup_id: int) -> Optional[DynamicRoadmap]:
        """Advances current day forward by 1 within dynamic roadmap duration."""
        roadmap = StartupRepository.get_roadmap(startup_id)
        if not roadmap:
            return None

        new_day = min(roadmap.total_duration_days, roadmap.current_day + 1)
        # Determine the phase matching new_day
        new_phase = roadmap.current_phase
        if roadmap.tasks:
            tasks_for_day = [t.phase for t in roadmap.tasks if t.day_number <= new_day and t.phase]
            if tasks_for_day:
                new_phase = tasks_for_day[-1]

        StartupRepository.update_roadmap_progress(
            roadmap_id=roadmap.id,
            current_day=new_day,
            current_phase=new_phase,
            progress_percent=None,  # will recompute from tasks
        )
        return StartupRepository.get_roadmap(startup_id)

    @staticmethod
    def complete_day(startup_id: int, day_number: int) -> Optional[DynamicRoadmap]:
        """Marks all tasks for the specified day as completed and updates progress."""
        roadmap = StartupRepository.get_roadmap(startup_id)
        if not roadmap:
            return None

        StartupRepository.complete_day_tasks(roadmap.id, day_number)
        return StartupRepository.get_roadmap(startup_id)

    @staticmethod
    def calculate_phase_progress(roadmap: DynamicRoadmap) -> Dict[str, Dict[str, Any]]:
        """Calculates completed vs total tasks per phase."""
        if not roadmap or not roadmap.tasks:
            return {}

        phases: Dict[str, Dict[str, Any]] = {}
        for task in roadmap.tasks:
            phase = task.phase or "Core Execution"
            if phase not in phases:
                phases[phase] = {"total": 0, "completed": 0}
            phases[phase]["total"] += 1
            if task.is_completed:
                phases[phase]["completed"] += 1

        for p_name, data in phases.items():
            tot = data["total"]
            done = data["completed"]
            data["percent"] = round((done / tot) * 100.0, 1) if tot > 0 else 0.0

        return phases
