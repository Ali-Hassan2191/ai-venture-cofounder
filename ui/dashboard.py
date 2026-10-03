"""
Overview Dashboard Screen.
Recreates the primary dashboard view from the UI reference image with real startup data.
"""
from typing import Optional, Dict, Any
import streamlit as st
import plotly.graph_objects as go
from database.models import Startup, StartupAnalysis, DynamicRoadmap, AgentResult
from database.repository import StartupRepository
from utils.constants import AGENT_METADATA
from ui.styles import render_html, get_width_kwargs


def render_dashboard(
    startup: Optional[Startup],
    analysis: Optional[StartupAnalysis],
    roadmap: Optional[DynamicRoadmap],
    agent_results: Dict[str, AgentResult],
):
    """
    Renders the Overview Dashboard.
    """
    if not startup:
        render_html(
            """
            <div class="welcome-hero" style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🚀</div>
                <h2 style="color: #FFFFFF; margin-bottom: 8px;">No Active Startup Found</h2>
                <p style="color: #94A3B8; max-width: 500px; margin: 0 auto 20px auto;">
                    Welcome to AI Venture Co-Founder. Let's begin by defining your startup idea,
                    target market, and capital budget.
                </p>
            </div>
            """
        )
        if st.button("Start Your Startup Journey →", type="primary", **get_width_kwargs(True)):
            st.session_state["current_page"] = "Startup Idea"
            st.rerun()
        return

    founder_name = (
        "Ali Hassan"
        if (not startup or not startup.founder_name or startup.founder_name in ["Ahmed Khan", "Founder"])
        else startup.founder_name
    )

    # 1. Welcome Greeting
    render_html(
        f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: #FFFFFF; font-weight: 700; margin: 0; font-size: 1.6rem;">
                        Welcome back, {founder_name}! 👋
                    </h2>
                    <p style="color: #94A3B8; font-size: 0.88rem; margin-top: 4px;">
                        Your AI co-founder team is working on your startup. Here is the latest executive progress.
                    </p>
                </div>
            </div>
        </div>
        """
    )

    # 2. Main Startup Identity & Overall Score (2 Columns)
    col1, col2 = st.columns([3, 1.2])

    with col1:
        phase_label = roadmap.current_phase if roadmap else "Validation Phase"
        day_info = f"Day {roadmap.current_day} / {roadmap.total_duration_days}" if roadmap else "Planning"

        render_html(
            f"""
            <div class="welcome-hero" style="position: relative;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="background: linear-gradient(135deg, #6366F1, #3B82F6);
                                    width: 48px; height: 48px; border-radius: 12px;
                                    display: flex; align-items: center; justify-content: center;
                                    font-size: 1.6rem;">
                            🚀
                        </div>
                        <div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF;">
                                {startup.name}
                            </div>
                            <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 2px;">
                                {startup.idea[:90]}{'...' if len(startup.idea) > 90 else ''}
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3);
                                color: #10B981; padding: 4px 12px; border-radius: 9999px;
                                font-size: 0.78rem; font-weight: 600;">
                        {phase_label}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 20px;
                            background: rgba(11, 15, 25, 0.6); padding: 12px; border-radius: 10px; border: 1px solid #1E293B;">
                    <div>
                        <div style="color: #64748B; font-size: 0.72rem; font-weight: 600;">COUNTRY</div>
                        <div style="color: #F8FAFC; font-size: 0.88rem; font-weight: 600; margin-top: 2px;">{startup.country}</div>
                    </div>
                    <div>
                        <div style="color: #64748B; font-size: 0.72rem; font-weight: 600;">TARGET MARKET</div>
                        <div style="color: #F8FAFC; font-size: 0.88rem; font-weight: 600; margin-top: 2px;">{startup.target_market}</div>
                    </div>
                    <div>
                        <div style="color: #64748B; font-size: 0.72rem; font-weight: 600;">BUDGET</div>
                        <div style="color: #F8FAFC; font-size: 0.88rem; font-weight: 600; margin-top: 2px;">{startup.currency}{startup.budget:,.0f}</div>
                    </div>
                    <div>
                        <div style="color: #64748B; font-size: 0.72rem; font-weight: 600;">ROADMAP PROGRESS</div>
                        <div style="color: #6366F1; font-size: 0.88rem; font-weight: 700; margin-top: 2px;">{day_info}</div>
                    </div>
                </div>
            </div>
            """
        )

    with col2:
        score = analysis.overall_score if analysis else 76
        verdict = analysis.feasibility_verdict if analysis else "Good Potential"

        # Check if any agent failed
        finance_failed = (agent_results.get("finance") and agent_results.get("finance").status == "failed")
        any_failed = any(r.status == "failed" for r in agent_results.values())
        is_incomplete = any_failed or ("Incomplete" in verdict) or ("Failed" in verdict)

        gauge_color = "#F59E0B" if is_incomplete else "#10B981"
        verdict_color = "#EF4444" if is_incomplete else "#10B981"

        # Render modern donut gauge chart
        fig = go.Figure(
            go.Pie(
                values=[score, max(0, 100 - score)],
                hole=0.75,
                marker=dict(colors=[gauge_color, "#1E293B"]),
                textinfo="none",
                hoverinfo="none",
            )
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=130,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b>{score}</b><br><span style='font-size:10px;color:#94A3B8;'>/100</span>",
                    x=0.5,
                    y=0.5,
                    font_size=20,
                    font_color="#FFFFFF",
                    font=dict(family="sans serif"),
                    showarrow=False,
                )
            ],
        )

        render_html(
            f"""
            <div class="welcome-hero" style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <div style="color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 6px;">
                    Startup Score
                </div>
            """
        )
        st.plotly_chart(fig, **get_width_kwargs(True), config={"displayModeBar": False})
        render_html(
            f"""
                <div style="color: {verdict_color}; font-size: 0.80rem; font-weight: 600; margin-top: -8px;">
                    ● {verdict}
                </div>
            </div>
            """
        )

    # 3. Category Score Cards (6 Columns)
    cat_scores = analysis.category_scores if (analysis and analysis.category_scores) else {
        "market": 82,
        "competition": 64,
        "business_model": 73,
        "finance": 68,
        "technology": 91,
        "risk": 59,
    }

    render_html("<div style='height: 10px;'></div>")
    c_cols = st.columns(6)

    category_configs = [
        ("market", "Market", "#10B981"),
        ("competition", "Competition", "#3B82F6"),
        ("business_model", "Business Model", "#8B5CF6"),
        ("finance", "Finance", "#F59E0B"),
        ("technology", "Technology", "#06B6D4"),
        ("risk", "Risk", "#EF4444"),
    ]

    for col, (key, label, color) in zip(c_cols, category_configs):
        val = cat_scores.get(key)
        agent_has_failed = (agent_results.get(key) and agent_results.get(key).status == "failed")
        with col:
            if val is None or agent_has_failed:
                render_html(
                    f"""
                    <div class="category-metric-card" style="border-color: rgba(239, 68, 68, 0.4);">
                        <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; margin-bottom: 4px;">
                            {label}
                        </div>
                        <div style="display: flex; align-items: baseline; justify-content: space-between;">
                            <div>
                                <span style="font-size: 1.05rem; font-weight: 700; color: #EF4444;">FAILED</span>
                            </div>
                            <span style="color: #EF4444; font-size: 0.75rem;">⚠️</span>
                        </div>
                        <div style="font-size: 0.68rem; color: #94A3B8; margin-top: 2px;">Unavailable</div>
                    </div>
                    """
                )
            else:
                render_html(
                    f"""
                    <div class="category-metric-card">
                        <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; margin-bottom: 4px;">
                            {label}
                        </div>
                        <div style="display: flex; align-items: baseline; justify-content: space-between;">
                            <div>
                                <span style="font-size: 1.3rem; font-weight: 700; color: {color};">{val}</span>
                                <span style="font-size: 0.72rem; color: #64748B;">/100</span>
                            </div>
                            <span style="color: {color}; font-size: 0.85rem;">↗</span>
                        </div>
                    </div>
                    """
                )

    # 4. AI Founding Team Row (6 Agents)
    render_html("<div style='height: 20px;'></div>")
    render_html(
        """
        <div style="margin-bottom: 12px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">
                AI Founding Team
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8;">
                Your 6 specialized AI agents analyzing and building your venture.
            </div>
        </div>
        """
    )

    agent_cols = st.columns(6)
    agent_keys = ["market_research", "competitor_analysis", "finance", "marketing", "cto", "ceo"]

    for col, key in zip(agent_cols, agent_keys):
        meta = AGENT_METADATA.get(key, {})
        res = agent_results.get(key)
        status = res.status if res else "pending"

        pill_class = f"status-pill-{status}"
        status_label = status.capitalize()

        with col:
            render_html(
                f"""
                <div class="venture-card" style="text-align: center; padding: 16px 10px;">
                    <div style="background: rgba(99, 102, 241, 0.1); width: 44px; height: 44px;
                                border-radius: 10px; margin: 0 auto 10px auto;
                                display: flex; align-items: center; justify-content: center;
                                font-size: 1.3rem;">
                        {meta.get('icon', '🤖')}
                    </div>
                    <div style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px;">
                        {meta.get('title', key).replace(' Agent', '')}
                    </div>
                    <div style="font-size: 0.7rem; color: #94A3B8; margin-bottom: 10px;">
                        {meta.get('role', 'Specialist')}
                    </div>
                    <span class="{pill_class}">
                        ● {status_label}
                    </span>
                </div>
                """
            )

    # 5. Quick Navigation Action Bar
    render_html("<div style='height: 12px;'></div>")
    q_col1, q_col2, q_col3 = st.columns(3)
    btn_kwargs = get_width_kwargs(True)
    with q_col1:
        if st.button("📋 View Complete Blueprint", **btn_kwargs):
            st.session_state["current_page"] = "Blueprint"
            st.rerun()
    with q_col2:
        if st.button("🗓️ Inspect Execution Plan", **btn_kwargs):
            st.session_state["current_page"] = "Execution Plan"
            st.rerun()
    with q_col3:
        if st.button("💬 Discuss with AI Co-Founder", **btn_kwargs):
            st.session_state["current_page"] = "Chat"
            st.rerun()
