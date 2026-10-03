"""
Competitor Analysis Screen.
Displays competitor landscape, product tear-downs, pricing models,
strengths, weaknesses, defensible USP, and positioning matrix.
"""
from typing import Optional, Dict, Any, List
import streamlit as st
import plotly.express as px
import pandas as pd
from database.models import Startup, AgentResult


def render_competitor_view(startup: Optional[Startup], agent_results: Dict[str, AgentResult]):
    """
    Renders the competitor intelligence screen.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                Competitive Landscape & Moats
            </h1>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                Direct and indirect market alternatives, pricing models, weaknesses, and unique positioning.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not startup:
        st.info("Please create or select a startup to view competitor analysis.")
        return

    comp_res = agent_results.get("competitor_analysis")
    data: Dict[str, Any] = comp_res.structured_output if (comp_res and comp_res.structured_output) else {}

    usp = data.get("recommended_usp", "Hyper-targeted localized pricing with batch delivery efficiency.")
    market_gaps = data.get("market_gaps") or [
        "No existing player offers campus-specific meal plan subscriptions.",
        "Incumbent platforms charge unaffordable delivery and convenience fees.",
        "Long delivery delays due to unstructured individual courier dispatches.",
    ]

    # USP Banner Card
    st.markdown(
        f"""
        <div class="welcome-hero" style="border-left: 4px solid #6366F1;">
            <div style="font-size: 0.8rem; color: #6366F1; font-weight: 700; text-transform: uppercase;">
                Defensible Unique Selling Proposition (USP)
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-top: 6px;">
                {usp}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Competitor Breakdown Cards
    st.markdown("### 👥 Competitor Dissection")
    raw_competitors = data.get("competitors") or [
        {
            "name": "Incumbent City Delivery Apps",
            "type": "Direct Legacy Player",
            "products_services": "Broad on-demand restaurant delivery",
            "pricing": "$3.99 - $5.99 delivery fee + 15% service markup",
            "strengths": ["Massive restaurant selection", "High brand recognition"],
            "weaknesses": ["Prohibitive pricing for students", "No dorm drop-off coordination"],
            "target_customers": "General urban affluent consumers",
        },
        {
            "name": "On-Campus Dining Halls",
            "type": "Indirect Alternative",
            "products_services": "Institutional meal cards and buffet plans",
            "pricing": "High fixed semester fee (~$2,500/semester)",
            "strengths": ["Immediate proximity", "Pre-paid by tuition"],
            "weaknesses": ["Repetitive menu options", "Limited operating hours"],
            "target_customers": "On-campus freshman dormitory students",
        },
    ]

    for comp in raw_competitors:
        name = comp.get("name", "Competitor")
        c_type = comp.get("type", "Market Player")
        pricing = comp.get("pricing", "Standard pricing")
        strengths = comp.get("strengths", [])
        weaknesses = comp.get("weaknesses", [])

        st.markdown(
            f"""
            <div class="venture-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">{name}</div>
                        <div style="font-size: 0.78rem; color: #3B82F6; font-weight: 600;">{c_type}</div>
                    </div>
                    <div style="background: #111726; border: 1px solid #1E293B; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #F59E0B; font-weight: 600;">
                        {pricing}
                    </div>
                </div>
                <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;">
                    {comp.get('products_services', '')}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.82rem;">
                    <div>
                        <div style="color: #10B981; font-weight: 700; margin-bottom: 4px;">Key Strengths:</div>
                        {''.join([f'<div style="color: #E2E8F0;">• {s}</div>' for s in strengths])}
                    </div>
                    <div>
                        <div style="color: #EF4444; font-weight: 700; margin-bottom: 4px;">Vulnerabilities / Weaknesses:</div>
                        {''.join([f'<div style="color: #E2E8F0;">• {w}</div>' for w in weaknesses])}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Market Positioning Matrix (Plotly Scatter Chart)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Strategic Positioning Map")

    pos_df = pd.DataFrame([
        {"Entity": f"{startup.name} (Us)", "Affordability (1-10)": 9.2, "Hyper-local Focus (1-10)": 9.5, "Size": 25, "Color": "#10B981"},
        {"Entity": "Legacy Delivery Giants", "Affordability (1-10)": 3.5, "Hyper-local Focus (1-10)": 3.0, "Size": 20, "Color": "#EF4444"},
        {"Entity": "Campus Dining Halls", "Affordability (1-10)": 5.0, "Hyper-local Focus (1-10)": 8.0, "Size": 18, "Color": "#3B82F6"},
        {"Entity": "Independent Courier Services", "Affordability (1-10)": 6.5, "Hyper-local Focus (1-10)": 4.5, "Size": 15, "Color": "#F59E0B"},
    ])

    fig = px.scatter(
        pos_df,
        x="Affordability (1-10)",
        y="Hyper-local Focus (1-10)",
        text="Entity",
        size="Size",
        color="Entity",
        color_discrete_map={
            f"{startup.name} (Us)": "#10B981",
            "Legacy Delivery Giants": "#EF4444",
            "Campus Dining Halls": "#3B82F6",
            "Independent Courier Services": "#F59E0B",
        },
    )
    fig.update_traces(textposition="top center", textfont=dict(color="#F8FAFC", size=11))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111726",
        showlegend=False,
        height=320,
        xaxis=dict(range=[1, 11], gridcolor="#1E293B", color="#94A3B8", title="Price Affordability & Economics →"),
        yaxis=dict(range=[1, 11], gridcolor="#1E293B", color="#94A3B8", title="Campus / Local Customization →"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4. Exploitable Market Gaps
    st.markdown("### 🚀 Critical Market Gaps")
    for gap in market_gaps:
        st.markdown(
            f"""
            <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid #6366F1; padding: 10px 14px; margin-bottom: 6px; border-radius: 4px; font-size: 0.88rem; color: #FFFFFF;">
                ✓ {gap}
            </div>
            """,
            unsafe_allow_html=True,
        )
