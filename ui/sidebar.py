"""
Sidebar navigation component.
Renders navigation items, active startup selector, token budget indicator, and founder profile.
"""
from typing import Optional, List
import streamlit as st
from utils.constants import NAV_ITEMS, APP_NAME
from database.models import Startup
from config.llm_config import global_token_manager, get_llm_config
from rag.faiss_manager import faiss_manager


def render_sidebar(startups: List[Startup], active_startup: Optional[Startup]) -> str:
    """
    Renders the dark sidebar and returns the currently selected page key.
    """
    with st.sidebar:
        # 1. Branding Header
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 12px 6px 20px 6px;">
                <div style="background: linear-gradient(135deg, #6366F1, #3B82F6);
                            width: 38px; height: 38px; border-radius: 10px;
                            display: flex; align-items: center; justify-content: center;
                            font-size: 1.3rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);">
                    🚀
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF; letter-spacing: -0.02em;">
                        {APP_NAME}
                    </div>
                    <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 500;">
                        AI Founding Suite
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Startup Selector (if startups exist)
        if startups:
            options = {s.id: f"{s.name} ({s.country})" for s in startups}
            current_id = active_startup.id if active_startup else startups[0].id
            default_index = (
                list(options.keys()).index(current_id)
                if current_id in options
                else 0
            )

            selected_id = st.selectbox(
                "Active Startup",
                options=list(options.keys()),
                format_func=lambda x: options[x],
                index=default_index,
                label_visibility="collapsed",
            )
            if selected_id != current_id:
                st.session_state["selected_startup_id"] = selected_id
                st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 3. Navigation List
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "Overview"

        nav_labels = [item[0] for item in NAV_ITEMS]
        current_nav = st.session_state["current_page"]
        default_nav_idx = nav_labels.index(current_nav) if current_nav in nav_labels else 0

        # Render styled radio navigation
        page = st.radio(
            "Navigation",
            options=nav_labels,
            index=default_nav_idx,
            label_visibility="collapsed",
        )
        st.session_state["current_page"] = page

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # 4. Token Budget Status (Global 7,500 token tracker)
        budget_summary = global_token_manager.get_summary()
        used = budget_summary["total_used"]
        total = budget_summary["max_total_tokens"]
        pct = budget_summary["usage_percent"]

        st.markdown(
            f"""
            <div style="background: #111726; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94A3B8; margin-bottom: 4px;">
                    <span>OUTPUT TOKEN BUDGET</span>
                    <span style="color: #6366F1; font-weight: 600;">{used:,} / {total:,}</span>
                </div>
                <div style="background: #1E293B; border-radius: 4px; height: 5px; width: 100%; overflow: hidden;">
                    <div style="background: #6366F1; height: 100%; width: {min(100, pct)}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 5. Founder Profile at Sidebar Footer
        founder_name = active_startup.founder_name if (active_startup and active_startup.founder_name) else "Ahmed Khan"
        st.markdown(
            f"""
            <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid #1E293B; display: flex; align-items: center; gap: 10px;">
                <div style="background: #3B82F6; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; color: #FFFFFF;">
                    {founder_name[0] if founder_name else 'F'}
                </div>
                <div style="line-height: 1.2;">
                    <div style="font-size: 0.85rem; font-weight: 600; color: #FFFFFF;">
                        {founder_name}
                    </div>
                    <div style="font-size: 0.72rem; color: #94A3B8;">
                        Founder
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return page
