"""
Startup Service.
Handles business logic for startup creation, retrieval, and validation.
"""
from typing import Optional, List, Tuple
from database.models import Startup
from database.repository import StartupRepository
from utils.validators import validate_startup_inputs, sanitize_text


class StartupService:

    @staticmethod
    def create_startup(
        name: str,
        idea: str,
        country: str,
        target_market: str,
        target_customer: str,
        budget: float,
        currency: str = "$",
        founder_name: str = "Founder",
        founder_experience: str = "Beginner",
        additional_context: str = "",
    ) -> Tuple[Optional[Startup], List[str]]:
        """
        Validates and persists a new startup venture.
        Returns (startup, errors).
        """
        is_valid, errors = validate_startup_inputs(
            name=name,
            idea=idea,
            country=country,
            target_customer=target_customer,
            budget=budget,
            founder_experience=founder_experience,
        )

        if not is_valid:
            return None, errors

        startup = Startup(
            name=sanitize_text(name),
            idea=sanitize_text(idea),
            country=sanitize_text(country),
            target_market=sanitize_text(target_market),
            target_customer=sanitize_text(target_customer),
            budget=float(budget),
            currency=currency or "$",
            founder_name=sanitize_text(founder_name) or "Founder",
            founder_experience=founder_experience or "Beginner",
            additional_context=sanitize_text(additional_context),
            status="created",
        )

        startup_id = StartupRepository.create_startup(startup)
        startup.id = startup_id
        return startup, []

    @staticmethod
    def get_startup(startup_id: int) -> Optional[Startup]:
        return StartupRepository.get_startup(startup_id)

    @staticmethod
    def get_active_or_latest_startup() -> Optional[Startup]:
        return StartupRepository.get_latest_startup()

    @staticmethod
    def list_all_startups() -> List[Startup]:
        return StartupRepository.list_startups()
