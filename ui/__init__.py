"""
UI package initialization.
Exports all UI render views and theme styling.
"""
from ui.styles import apply_theme, render_html, get_width_kwargs
from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard
from ui.startup_form import render_startup_form
from ui.agents_view import render_agents_view
from ui.market_view import render_market_view
from ui.competitor_view import render_competitor_view
from ui.finance_view import render_finance_view
from ui.blueprint_view import render_blueprint_view
from ui.execution_view import render_execution_view
from ui.progress_view import render_progress_view
from ui.chat_view import render_chat_view
from ui.reports_view import render_reports_view

__all__ = [
    "apply_theme",
    "render_html",
    "render_sidebar",
    "render_dashboard",
    "render_startup_form",
    "render_agents_view",
    "render_market_view",
    "render_competitor_view",
    "render_finance_view",
    "render_blueprint_view",
    "render_execution_view",
    "render_progress_view",
    "render_chat_view",
    "render_reports_view",
]
