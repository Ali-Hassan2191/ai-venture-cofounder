"""
Custom CSS styling for AI Venture Co-Founder.
Recreates the modern dark dashboard aesthetic shown in the UI reference image.
"""

DARK_THEME_CSS = """
<style>
/* Global reset and dark palette */
:root {
    --bg-primary: #0B0F19;
    --bg-card: #131927;
    --bg-card-hover: #1A2238;
    --border-color: #1E293B;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --accent-indigo: #6366F1;
    --accent-blue: #3B82F6;
    --accent-emerald: #10B981;
    --accent-amber: #F59E0B;
    --accent-rose: #EF4444;
}

/* Background */
.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0D121F !important;
    border-right: 1px solid var(--border-color);
}

/* Card components */
.venture-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.2s ease-in-out;
}
.venture-card:hover {
    border-color: #334155;
    background: var(--bg-card-hover);
}

/* Welcome Card */
.welcome-hero {
    background: linear-gradient(135deg, #131B2E 0%, #161F36 100%);
    border: 1px solid #23304B;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
}

/* Score Pills and Badges */
.score-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
}
.status-pill-completed {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-pill-running {
    background: rgba(59, 130, 246, 0.15);
    color: #3B82F6;
    border: 1px solid rgba(59, 130, 246, 0.3);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-pill-pending {
    background: rgba(148, 163, 184, 0.1);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.2);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-pill-failed {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Metrics and Values */
.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
}
.stat-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

/* Category Mini Card */
.category-metric-card {
    background: #111726;
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 14px;
    text-align: left;
}

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

/* Hide default streamlit header clutter */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""


def apply_theme():
    """Applies the dark aesthetic styling via streamlit markdown."""
    import streamlit as st
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


def render_html(html_str: str) -> None:
    """
    Renders raw HTML safely in Streamlit without Markdown interpreting
    blank lines or indented tags as code blocks (<pre><code>).
    """
    import textwrap
    import streamlit as st
    cleaned = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def get_width_kwargs(stretch: bool = True) -> dict:
    """
    Returns compatibility kwargs for Streamlit width.
    Uses width='stretch' on newer Streamlit versions (1.65+) to eliminate deprecation warnings,
    and falls back to use_container_width on older Streamlit versions.
    """
    import inspect
    import streamlit as st
    try:
        sig = inspect.signature(st.plotly_chart)
        if "width" in sig.parameters:
            return {"width": "stretch" if stretch else "content"}
    except Exception:
        pass
    return {"use_container_width": stretch}

