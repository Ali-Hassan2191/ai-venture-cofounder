"""
AI Founding Team (Agents) Screen.
Recreates the dedicated agents screen from the UI reference image.
"""
from typing import Dict, Any, Optional
import streamlit as st
from database.models import Startup, AgentResult
from utils.constants import AGENT_METADATA


def render_agents_view(startup: Optional[Startup], agent_results: Dict[str, AgentResult]):
    """
    Renders the 6 specialized AI co-founder agent cards.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                AI Founding Team
            </h1>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                6 specialized agents working together to build and evaluate your startup.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not startup:
        st.info("Please create or select a startup venture to view agent outputs.")
        return

    agent_keys = ["market_research", "competitor_analysis", "finance", "marketing", "cto", "ceo"]

    for key in agent_keys:
        meta = AGENT_METADATA.get(key, {})
        res = agent_results.get(key)
        status = res.status if res else "pending"
        tokens = res.tokens_used if res else 0

        pill_class = f"status-pill-{status}"
        status_label = status.capitalize()

        with st.container():
            st.markdown(
                f"""
                <div class="venture-card" style="display: flex; justify-content: space-between; align-items: center; padding: 18px 24px;">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="background: rgba(99, 102, 241, 0.15); width: 48px; height: 48px;
                                    border-radius: 12px; display: flex; align-items: center;
                                    justify-content: center; font-size: 1.5rem;">
                            {meta.get('icon', '🤖')}
                        </div>
                        <div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">
                                {meta.get('title', key)}
                            </div>
                            <div style="color: #94A3B8; font-size: 0.82rem; margin-top: 2px;">
                                {meta.get('description', '')}
                            </div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <span style="color: #64748B; font-size: 0.78rem;">
                            {tokens:,} tokens
                        </span>
                        <span class="{pill_class}">
                            ● {status_label}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Details expander
            with st.expander(f"View Details: {meta.get('title', key)}"):
                if res and (res.structured_output or res.raw_output):
                    tab1, tab2 = st.tabs(["Structured Intelligence", "Executive Raw Output"])
                    with tab1:
                        st.json(res.structured_output)
                    with tab2:
                        st.markdown(f"```text\n{res.raw_output}\n```")
                else:
                    st.write("Agent has not yet been executed for this venture. Run analysis from the Startup Idea screen.")
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
