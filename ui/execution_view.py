"""
Execution Plan Screen.
Features dynamic venture-calibrated roadmap duration, phased day sequence,
interactive task completion, real-time SQLite persistence, and strategic co-founder guidance.
"""
from typing import Optional
import streamlit as st
import plotly.graph_objects as go
from database.models import Startup, DynamicRoadmap, RoadmapTask, StartupAnalysis
from database.repository import StartupRepository
from services.roadmap_service import RoadmapService
from ui.styles import get_width_kwargs


def render_execution_view(
    startup: Optional[Startup],
    roadmap: Optional[DynamicRoadmap],
    analysis: Optional[StartupAnalysis] = None,
):
    """
    Renders the dynamic Execution Plan screen.
    """
    if not startup or not roadmap:
        st.info("No active execution roadmap found. Run startup analysis to generate a calibrated dynamic roadmap.")
        return

    if analysis is None:
        analysis = StartupRepository.get_analysis(startup.id)

    total_days = roadmap.total_duration_days
    current_day = max(1, min(total_days, roadmap.current_day))
    progress_pct = roadmap.progress_percent

    # Ensure view_day in session_state defaults to current_day
    view_key = f"view_day_{startup.id}"
    if view_key not in st.session_state or st.session_state[view_key] > total_days:
        st.session_state[view_key] = current_day
    view_day = st.session_state[view_key]

    tasks = roadmap.tasks or []

    # 1. Header with Duration & Overall Progress Bar
    h_col1, h_col2 = st.columns([2.5, 1.5])
    with h_col1:
        st.markdown(
            f"""
            <div>
                <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                    Execution Plan
                </h1>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                    Your <b>{total_days}-day</b> venture roadmap with day-by-day deliverables and progress tracking.
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
                        🗓️ Active: Day {current_day} / {total_days}
                    </span>
                    <span style="color: #10B981; font-weight: 700; font-size: 0.85rem;">
                        {progress_pct:.0f}% Complete
                    </span>
                </div>
                <div style="background: #1E293B; border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
                    <div style="background: #10B981; height: 100%; width: {min(100.0, max(4.0, progress_pct))}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Dynamic Timeline Sequence (Sliding 7-day window centered on current_day)
    st.markdown(
        """
        <div style="font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px;">
            Execution Timeline (Calibrated Venture Roadmap)
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Compute a 7-day sliding window
    window_size = min(7, total_days)
    start_d = max(1, min(current_day - 3, total_days - window_size + 1))
    end_d = min(total_days, start_d + window_size - 1)
    window_days = list(range(start_d, end_d + 1))

    t_cols = st.columns(len(window_days))
    for col, d_num in zip(t_cols, window_days):
        # Determine status for this day
        if d_num < current_day:
            d_state = "completed"
            border_css = "border: 1px solid rgba(16, 185, 129, 0.4);"
            bg_css = "background: rgba(16, 185, 129, 0.1);"
            badge_color = "#10B981"
            badge_icon = "✓ Done"
        elif d_num == current_day:
            d_state = "active"
            border_css = "border: 2px solid #6366F1;"
            bg_css = "background: rgba(99, 102, 241, 0.22);"
            badge_color = "#818CF8"
            badge_icon = "● Active"
        else:
            d_state = "pending"
            border_css = "border: 1px solid #1E293B;"
            bg_css = "background: #111726;"
            badge_color = "#64748B"
            badge_icon = "○ Upcoming"

        # Find day label from tasks or phase
        d_tasks = [t for t in tasks if t.day_number == d_num]
        if d_tasks and d_tasks[0].title:
            raw_title = d_tasks[0].title
            d_label = (raw_title[:14] + "..") if len(raw_title) > 15 else raw_title
        elif d_num <= round(total_days * 0.25):
            d_label = "Validation"
        elif d_num <= round(total_days * 0.60):
            d_label = "Core Build"
        elif d_num <= round(total_days * 0.85):
            d_label = "Pilot Launch"
        else:
            d_label = "Scaling"

        is_viewing = (d_num == view_day)
        extra_border = "box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);" if is_viewing else ""

        with col:
            st.markdown(
                f"""
                <div style="{bg_css} {border_css} {extra_border} border-radius: 8px; padding: 10px 4px; text-align: center; cursor: pointer;">
                    <div style="font-size: 0.70rem; color: {badge_color}; font-weight: 700;">{badge_icon}</div>
                    <div style="font-size: 0.74rem; color: #94A3B8; font-weight: 600; margin-top: 2px;">Day {d_num}</div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: #FFFFFF; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{d_tasks[0].title if d_tasks else d_label}">{d_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"View Day {d_num}", key=f"btn_day_{d_num}", **get_width_kwargs(True)):
                st.session_state[view_key] = d_num
                st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. Selected Day Execution Card
    view_day_tasks = [t for t in tasks if t.day_number == view_day]
    # Fallback to closest available tasks if this specific day has no separate row
    display_tasks = view_day_tasks if view_day_tasks else [t for t in tasks if abs(t.day_number - view_day) <= 2][:3]

    completed_count = sum(1 for t in display_tasks if t.is_completed)
    total_count = len(display_tasks)
    if total_count > 0:
        day_pct = round((completed_count / total_count * 100))
    elif view_day < current_day:
        day_pct = 100
    else:
        day_pct = 0

    # Determine phase label for view_day
    if view_day_tasks and view_day_tasks[0].phase:
        day_phase = view_day_tasks[0].phase
    elif view_day <= round(total_days * 0.22):
        day_phase = "Phase 1: Validation & Customer Discovery"
    elif view_day <= round(total_days * 0.60):
        day_phase = "Phase 2: Core Architecture & Build"
    elif view_day <= round(total_days * 0.85):
        day_phase = "Phase 3: Pilot & Unit Economics Validation"
    else:
        day_phase = "Phase 4: Commercial Launch & Scaling"

    # Status tag
    if view_day == current_day:
        pill_html = '<span class="status-pill-running">● Current Active Day</span>'
    elif view_day < current_day:
        pill_html = '<span style="background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 10px; border-radius: 9999px; font-size: 0.78rem; font-weight: 600;">✓ Completed Day</span>'
    else:
        pill_html = '<span style="background: rgba(100, 116, 139, 0.15); color: #94A3B8; border: 1px solid #1E293B; padding: 3px 10px; border-radius: 9999px; font-size: 0.78rem; font-weight: 600;">○ Upcoming Sprint</span>'

    st.markdown(
        f"""
        <div class="venture-card" style="border-top: 3px solid #6366F1; padding: 22px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                        Day {view_day} – {day_phase}
                    </div>
                    {pill_html}
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
                Scheduled Action Items
            </div>
            """,
            unsafe_allow_html=True,
        )

        if display_tasks:
            for task in display_tasks:
                key_id = f"task_chk_{task.id}_{task.day_number}"
                is_done = st.checkbox(f"**{task.title}**", value=task.is_completed, key=key_id)
                if task.description:
                    st.markdown(
                        f"<div style='color: #94A3B8; font-size: 0.78rem; margin-left: 28px; margin-top: -6px; margin-bottom: 10px; line-height: 1.4;'>{task.description}</div>",
                        unsafe_allow_html=True,
                    )
                if is_done != task.is_completed:
                    RoadmapService.toggle_task(task.id, is_done)
                    st.rerun()
        else:
            st.markdown(
                f"""
                <div style="background: rgba(99, 102, 241, 0.05); border: 1px dashed #1E293B; border-radius: 8px; padding: 14px; color: #94A3B8; font-size: 0.82rem;">
                    Focus sprint: Dedicated development & execution block for <b>{day_phase}</b>.
                    Complete active action items or advance to the next scheduled deliverable.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with c2:
        # Donut completion chart for today
        donut = go.Figure(go.Pie(
            values=[day_pct, max(0, 100 - day_pct)],
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
        st.markdown("<div style='text-align: center; color: #94A3B8; font-size: 0.75rem; font-weight: 600;'>DAY COMPLETION</div>", unsafe_allow_html=True)
        st.plotly_chart(donut, **get_width_kwargs(True), config={"displayModeBar": False})

    with c3:
        # Dynamic Co-Founder Note based on the startup's real analysis and active day
        if analysis and analysis.recommended_next_steps:
            step_idx = min(len(analysis.recommended_next_steps) - 1, max(0, (view_day - 1) % len(analysis.recommended_next_steps)))
            cofounder_note = analysis.recommended_next_steps[step_idx]
        elif display_tasks and display_tasks[0].description:
            cofounder_note = display_tasks[0].description
        else:
            cofounder_note = f"Focus on executing Day {view_day} deliverables for {startup.name}. Validate assumptions directly with {startup.target_customer}."

        st.markdown(
            f"""
            <div style="background: #111726; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">
                    Today's Co-Founder Note
                </div>
                <div style="font-size: 0.82rem; color: #E2E8F0; margin-top: 6px; line-height: 1.4;">
                    {cofounder_note}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if display_tasks and st.button("✓ Mark Done", **get_width_kwargs(True)):
                RoadmapService.complete_day(startup.id, view_day)
                st.rerun()
        with b_col2:
            if st.button("Advance Day →", type="primary", **get_width_kwargs(True)):
                RoadmapService.advance_day(startup.id)
                st.session_state[view_key] = min(total_days, current_day + 1)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Dynamic Next Step Alert Card (matching the active startup's real roadmap)
    next_day_num = min(total_days, current_day + 1)
    next_day_tasks = [t for t in tasks if t.day_number == next_day_num]

    if next_day_tasks:
        next_step_title = next_day_tasks[0].title
        next_step_desc = next_day_tasks[0].description or f"Execute scheduled Day {next_day_num} deliverables for {startup.name}."
    elif analysis and analysis.recommended_next_steps:
        next_step_title = f"{day_phase} Progression"
        next_step_desc = analysis.recommended_next_steps[min(len(analysis.recommended_next_steps) - 1, current_day % len(analysis.recommended_next_steps))]
    else:
        next_step_title = f"Phase Progression"
        next_step_desc = f"Advance to Day {next_day_num} deliverables for {startup.target_market}."

    st.markdown(
        f"""
        <div class="welcome-hero" style="border: 1px solid #F59E0B; background: rgba(245, 158, 11, 0.05); padding: 16px 20px; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="font-size: 1.6rem;">💡</div>
                <div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F59E0B; text-transform: uppercase;">
                        Next Step (Day {next_day_num} / {total_days})
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #FFFFFF; margin-top: 2px;">
                        {next_step_title} – <span style="font-weight: 400; color: #CBD5E1;">{next_step_desc}</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
