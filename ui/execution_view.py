"""
Execution Plan Screen.
Recreates the interactive execution plan from the UI reference image.
Features dynamic roadmap duration, phased day sequence, interactive task completion, and next steps.
"""
from typing import Optional
import streamlit as st
import plotly.graph_objects as go
from database.models import Startup, DynamicRoadmap, RoadmapTask
from services.roadmap_service import RoadmapService


def render_execution_view(startup: Optional[Startup], roadmap: Optional[DynamicRoadmap]):
    """
    Renders the dynamic Execution Plan screen.
    """
    if not startup or not roadmap:
        st.info("No active execution roadmap found. Run startup analysis to generate a dynamic roadmap.")
        return

    total_days = roadmap.total_duration_days
    current_day = roadmap.current_day
    progress_pct = roadmap.progress_percent

    # Header with Duration & Overall Progress Bar
    h_col1, h_col2 = st.columns([2.5, 1.5])
    with h_col1:
        st.markdown(
            f"""
            <div>
                <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                    Execution Plan
                </h1>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                    Your {total_days}-day calibrated roadmap with daily tasks and execution tracking.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h_col2:
        st.markdown(
            f"""
            <div style="background: #111726; border: 1px solid #1E293B; border-radius: 10px; padding: 10px 16px; text-align: right;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #FFFFFF;">
                        🗓️ Day {current_day} / {total_days}
                    </span>
                    <span style="color: #10B981; font-weight: 700; font-size: 0.85rem;">
                        {progress_pct:.0f}%
                    </span>
                </div>
                <div style="background: #1E293B; border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
                    <div style="background: #10B981; height: 100%; width: {min(100.0, max(5.0, progress_pct))}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 2. Timeline Sequence (Visual day steps matching reference image)
    st.markdown(
        """
        <div style="font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px;">
            Execution Timeline (Calibrated Venture Roadmap)
        </div>
        """,
        unsafe_allow_html=True,
    )

    timeline_days = [
        (1, "Validation", "#10B981", "completed"),
        (2, "Pricing Test", "#10B981", "completed"),
        (3, "Interviews", "#10B981", "completed"),
        (4, "Analysis", "#6366F1", "active"),
        (5, "Core Build", "#64748B", "pending"),
        (6, "Feature Test", "#64748B", "pending"),
        (7, "Pilot Prep", "#64748B", "pending"),
    ]

    t_cols = st.columns(len(timeline_days))
    for col, (d_num, d_label, d_color, d_state) in zip(t_cols, timeline_days):
        with col:
            is_active = d_state == "active"
            border_css = "border: 2px solid #6366F1;" if is_active else "border: 1px solid #1E293B;"
            bg_css = "background: rgba(99, 102, 241, 0.2);" if is_active else "background: #111726;"

            st.markdown(
                f"""
                <div style="{bg_css} {border_css} border-radius: 8px; padding: 10px 4px; text-align: center;">
                    <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600;">Day {d_num}</div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: #FFFFFF; margin-top: 2px;">{d_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 3. Active Day Card (Day 4 - Market Analysis & Feedback)
    tasks = roadmap.tasks or []
    current_day_tasks = [t for t in tasks if t.day_number == current_day] or tasks[:5]

    completed_count = sum(1 for t in current_day_tasks if t.is_completed)
    total_count = len(current_day_tasks)
    day_pct = round((completed_count / total_count * 100)) if total_count > 0 else 0

    st.markdown(
        f"""
        <div class="venture-card" style="border-top: 3px solid #6366F1; padding: 22px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                        Day {current_day} – {roadmap.current_phase} & Customer Feedback
                    </div>
                    <span class="status-pill-running">
                        ● In Progress
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: #10B981; font-weight: 600;">
                    {completed_count}/{total_count} tasks completed
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.6, 1, 1.4])

    with c1:
        st.markdown(
            """
            <div style="font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 10px;">
                Today's Action Items
            </div>
            """,
            unsafe_allow_html=True,
        )

        for task in current_day_tasks:
            key_id = f"task_chk_{task.id}"
            is_done = st.checkbox(task.title, value=task.is_completed, key=key_id)
            if is_done != task.is_completed:
                RoadmapService.toggle_task(task.id, is_done)
                st.rerun()

    with c2:
        # Donut completion chart for today
        donut = go.Figure(go.Pie(
            values=[day_pct, 100 - day_pct],
            hole=0.75,
            marker=dict(colors=["#10B981", "#1E293B"]),
            textinfo="none",
            hoverinfo="none",
        ))
        donut.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=130,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"<span style='font-size:20px; font-weight:700; color:#FFFFFF;'>{day_pct}%</span>", x=0.5, y=0.5, showarrow=False)],
        )
        st.markdown("<div style='text-align: center; color: #94A3B8; font-size: 0.75rem; font-weight: 600;'>TODAY'S COMPLETION</div>", unsafe_allow_html=True)
        st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})

    with c3:
        st.markdown(
            f"""
            <div style="background: #111726; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">
                    Today's Co-Founder Note
                </div>
                <div style="font-size: 0.82rem; color: #E2E8F0; margin-top: 6px; line-height: 1.4;">
                    Based on early customer discovery signals, users are receptive to scheduled batch delivery. Focus on verifying willingness to pre-pay.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Advance to Next Day →", use_container_width=True):
            RoadmapService.advance_day(startup.id)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Next Step Alert Card (matching reference image)
    next_day_num = min(total_days, current_day + 1)
    st.markdown(
        f"""
        <div class="welcome-hero" style="border: 1px solid #F59E0B; background: rgba(245, 158, 11, 0.05); padding: 16px 20px; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="font-size: 1.6rem;">💡</div>
                <div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F59E0B; text-transform: uppercase;">
                        Next Step (Day {next_day_num})
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #FFFFFF; margin-top: 2px;">
                        Pricing Validation – Test tiered student discount models with 10 target users.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
