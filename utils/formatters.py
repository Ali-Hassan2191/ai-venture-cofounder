"""
Formatting and presentation helpers for AI Venture Co-Founder.
"""
import re
import json
from typing import Any, Dict, Optional


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Formats numeric values into clean readable currency."""
    if amount is None:
        return "N/A"
    try:
        val = float(amount)
        if val >= 1_000_000:
            return f"{currency_symbol}{val / 1_000_000:.2f}M"
        if val >= 1_000:
            return f"{currency_symbol}{val:,.0f}"
        return f"{currency_symbol}{val:.2f}"
    except (ValueError, TypeError):
        return str(amount)


def format_score_badge(score: int) -> Dict[str, str]:
    """Returns color styling and qualitative label based on 0-100 score."""
    try:
        val = int(score)
    except (ValueError, TypeError):
        val = 0

    if val >= 80:
        return {"color": "#10B981", "label": "High Feasibility", "bg": "rgba(16, 185, 129, 0.15)"}
    elif val >= 65:
        return {"color": "#3B82F6", "label": "Good Potential", "bg": "rgba(59, 130, 246, 0.15)"}
    elif val >= 50:
        return {"color": "#F59E0B", "label": "Moderate / Pivot Advised", "bg": "rgba(245, 158, 11, 0.15)"}
    else:
        return {"color": "#EF4444", "label": "High Risk / Re-evaluate", "bg": "rgba(239, 68, 68, 0.15)"}


def clean_markdown_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely extracts and parses JSON from LLM output,
    handling markdown fences (```json ... ```) or embedded objects.
    """
    if not text:
        return None

    cleaned = text.strip()

    # Check for markdown code blocks
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, cleaned)
    if match:
        cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: attempt to find the outermost curly braces
        brace_match = re.search(r"(\{[\s\S]*\})", cleaned)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass
    return None


def truncate_text(text: str, max_length: int = 140) -> str:
    """Truncates text with ellipsis for card summaries."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."
