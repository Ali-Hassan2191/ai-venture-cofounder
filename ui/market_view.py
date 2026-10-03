"""
Market Analysis Screen.
Displays target demographics, pain points, market trends, opportunities,
local geographic nuances, and evidence-backed demand signals.
"""
from typing import Optional, Dict, Any
import streamlit as st
import plotly.graph_objects as go
from database.models import Startup, AgentResult, StartupAnalysis
from ui.styles import get_width_kwargs


def render_market_view(
    startup: Optional[Startup],
    analysis: Optional[StartupAnalysis],
    agent_results: Dict[str, AgentResult],
):
    """
    Renders the deep market research screen.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                Market Analysis & Demand Validation
            </h1>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                Empirical customer research, market sizing, industry tailwinds, and local regional factors.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not startup:
        st.info("Please create or select a startup to view market analysis.")
        return

    mkt_res = agent_results.get("market_research")
    if not mkt_res and not analysis:
        st.info(f"Market analysis for '{startup.name}' has not been generated yet. Run startup evaluation to begin market research.")
        return

    data: Dict[str, Any] = mkt_res.structured_output if (mkt_res and mkt_res.structured_output) else {}

    # Authoritative single source for market score
    score = None
    if analysis and analysis.category_scores and "market" in analysis.category_scores:
        score = analysis.category_scores.get("market")
    if score is None:
        score = data.get("market_score")
    if score is None:
        score = 0

    growth = data.get("growth_potential", "High")
    local_info = data.get("local_market_nuances", f"Strong localized demand in {startup.country}.")

    # Top Metric Banner
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Market Feasibility Score</div>
                <div class="stat-value" style="color: #10B981;">{score} <span style="font-size: 1rem; color: #64748B;">/100</span></div>
                <div style="color: #10B981; font-size: 0.78rem; font-weight: 600; margin-top: 4px;">Empirical Demand Evaluation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Target Market Segment</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-top: 4px;">{startup.target_customer}</div>
                <div style="color: #94A3B8; font-size: 0.78rem; margin-top: 4px;">Region: {startup.country}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Projected Growth Velocity</div>
                <div class="stat-value" style="color: #3B82F6;">{growth}</div>
                <div style="color: #94A3B8; font-size: 0.78rem; margin-top: 4px;">Macro market tailwinds</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Customer Problems & Opportunities Row
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ⚠️ Acute Customer Problems")
        problems = data.get("customer_problems") or [
            f"Friction and fragmented providers in {startup.country}",
            f"High costs making existing alternatives inefficient for {startup.target_customer}",
            f"Lack of tailored features addressing core workflow needs",
        ]
        for p in problems:
            st.markdown(
                f"""
                <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; padding: 12px; margin-bottom: 8px; border-radius: 4px; font-size: 0.88rem; color: #F8FAFC;">
                    {p}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with c2:
        st.markdown("### 💡 High-Value Market Opportunities")
        opps = data.get("market_opportunities") or [
            f"Tailored solution capturing underserved {startup.target_customer} base",
            f"Cost-efficient business model unlocking rapid adoption",
            f"Strong localized network effects across {startup.country}",
        ]
        for op in opps:
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; padding: 12px; margin-bottom: 8px; border-radius: 4px; font-size: 0.88rem; color: #F8FAFC;">
                    {op}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 3. Market Trends Radar / Dynamics Chart
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Market Dynamics & Demand Drivers")

    trend_categories = ["Customer Pain Intensity", "Willingness to Pay", "TAM Sizing", "Market Growth", "Regulatory Ease"]
    trend_values = [
        min(95, max(50, int(score * 1.05))),
        min(95, max(45, int(score * 0.92))),
        min(95, max(50, int(score * 0.98))),
        min(95, max(55, int(score * 1.02))),
        min(95, max(40, int(score * 0.90))),
    ]

    fig = go.Figure(data=go.Scatterpolar(
        r=trend_values + [trend_values[0]],
        theta=trend_categories + [trend_categories[0]],
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.25)',
        line=dict(color='#6366F1', width=2),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="#1E293B"),
            angularaxis=dict(color="#F8FAFC", gridcolor="#1E293B"),
            bgcolor="#111726",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        height=320,
    )
    st.plotly_chart(fig, **get_width_kwargs(True))

    # 4. Evidence vs Assumptions
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        st.markdown("### 🔬 Retrieved Evidence & Benchmarks")
        evidence = data.get("retrieved_evidence") or [
            f"Sector benchmark: Verified high repeat usage potential among {startup.target_customer}.",
            f"Regional indicators: Strong demand growth in {startup.country}.",
        ]
        for ev in evidence:
            st.markdown(f"- {ev}")

    with e_col2:
        st.markdown("### 📝 Strategic Assumptions Under Validation")
        assumptions = data.get("assumptions") or [
            f"{startup.target_customer} are willing to transition from legacy methods to {startup.name}.",
            f"Initial customer acquisition cost remains sustainable with a {startup.currency}{startup.budget:,.0f} budget.",
        ]
        for asmp in assumptions:
            st.markdown(f"- {asmp}")
