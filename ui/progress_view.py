"""
Progress Screen.
Visualizes venture progress, milestone completion, phased deliverables, and agent execution health.
"""
from typing import Optional, Dict
import streamlit as st
import plotly.graph_objects as go
from database.models import Startup, DynamicRoadmap, AgentResult
from services.roadmap_service import RoadmapService
from ui.styles import get_width_kwargs


def render_progress_view(
    startup: Optional[Startup],
    roadmap: Optional[DynamicRoadmap],
    agent_results: Dict[str, AgentResult],
):
    """
    Renders the execution progress screen.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                Venture Execution Progress
            </h1>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                Comprehensive milestone velocity, phase completion rates, and co-founder task status.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not startup or not roadmap:
        st.info("No active execution progress available yet. Launch startup analysis to begin tracking.")
        return

    phase_data = RoadmapService.calculate_phase_progress(roadmap)
    tasks = roadmap.tasks or []
    completed_tasks = [t for t in tasks if t.is_completed]
    pending_tasks = [t for t in tasks if not t.is_completed]

    # 1. High-Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Total Execution Progress</div>
                <div class="stat-value" style="color: #10B981;">{roadmap.progress_percent:.0f}%</div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Across {roadmap.total_duration_days} total days</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Completed Action Items</div>
                <div class="stat-value" style="color: #3B82F6;">{len(completed_tasks)}</div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Verified deliverables</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Pending Action Items</div>
                <div class="stat-value" style="color: #F59E0B;">{len(pending_tasks)}</div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Scheduled in pipeline</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        completed_agents = sum(1 for a in agent_results.values() if a.status == "completed")
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">AI Founding Agents</div>
                <div class="stat-value" style="color: #6366F1;">{completed_agents}/6</div>
                <div style="color: #10B981; font-size: 0.75rem; margin-top: 4px;">● Fully Active</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Phase Progress Horizontal Bars
    st.markdown("### 📊 Phase Completion Velocity")
    if phase_data:
        phases = list(phase_data.keys())
        pcts = [phase_data[p]["percent"] for p in phases]

        fig = go.Figure(go.Bar(
            x=pcts,
            y=phases,
            orientation='h',
            marker=dict(color="#6366F1"),
            text=[f"{p:.0f}%" for p in pcts],
            textposition="auto",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#111726",
            height=240,
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(range=[0, 100], gridcolor="#1E293B", color="#94A3B8", title="Completion %"),
            yaxis=dict(gridcolor="#1E293B", color="#F8FAFC"),
        )
        st.plotly_chart(fig, **get_width_kwargs(True))

    # 3. Phased Milestones Checklist (from active dynamic roadmap)
    st.markdown("### 🏆 Strategic Milestones Tracker")
    milestones = roadmap.milestones
    if not milestones:
        milestones = []
        for t in tasks:
            if t.milestone_tag:
                milestones.append({"day": t.day_number, "title": f"{t.milestone_tag} – {t.title}"})
    if not milestones:
        tot = roadmap.total_duration_days
        milestones = [
            {"day": max(3, round(tot * 0.22)), "title": f"Customer Validation Sign-Off ({startup.target_customer})"},
            {"day": max(7, round(tot * 0.60)), "title": f"Core Product Feature Complete for {startup.name}"},
            {"day": max(10, round(tot * 0.85)), "title": f"Pilot Alpha Cohort Review in {startup.country}"},
            {"day": tot, "title": f"Commercial Public Launch & Growth Gate"},
        ]

    for m in milestones:
        day_num = m.get("day", 1)
        is_past = roadmap.current_day >= day_num
        icon = "✅" if is_past else "⏳"
        color = "#10B981" if is_past else "#94A3B8"
        status_txt = "Achieved" if is_past else "Upcoming Target"

        st.markdown(
            f"""
            <div class="venture-card" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 20px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 1.2rem;">{icon}</span>
                    <div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">
                            Day {day_num}: {m.get('title')}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748B;">
                            Venture Execution Gate
                        </div>
                    </div>
                </div>
                <div style="color: {color}; font-weight: 600; font-size: 0.82rem;">
                    {status_txt}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
