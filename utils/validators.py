"""
Input validation utilities.
"""
from typing import Dict, Any, List, Tuple


def validate_startup_inputs(
    name: str,
    idea: str,
    country: str,
    target_customer: str,
    budget: float,
    founder_experience: str,
) -> Tuple[bool, List[str]]:
    """
    Validates user startup onboarding fields.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append("Startup name must be at least 2 characters long.")
    elif len(name.strip()) > 100:
        errors.append("Startup name must not exceed 100 characters.")

    if not idea or len(idea.strip()) < 15:
        errors.append("Please provide a more descriptive startup idea (at least 15 characters).")

    if not country or len(country.strip()) < 2:
        errors.append("Please specify a valid operating country or target market.")

    if not target_customer or len(target_customer.strip()) < 3:
        errors.append("Please define the primary target customer group.")

    if budget is None or budget < 0:
        errors.append("Initial capital/budget must be a non-negative number.")

    valid_experiences = ["Beginner", "Intermediate", "Experienced Serial Founder", "Domain Expert"]
    if founder_experience and founder_experience not in valid_experiences:
        # soft check, allow custom strings too if not empty
        if len(founder_experience.strip()) == 0:
            errors.append("Please select or specify founder experience level.")

    return len(errors) == 0, errors


def sanitize_text(text: str) -> str:
    """
    Strips harmful control characters and normalizes whitespace.
    """
    if not text:
        return ""
    return " ".join(text.split()).strip()
