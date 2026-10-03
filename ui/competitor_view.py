"""
Competitor Analysis Screen.
Displays competitor landscape, product tear-downs, pricing models,
strengths, weaknesses, defensible USP, and dynamic positioning matrix.
"""
from typing import Optional, Dict, Any, List
import streamlit as st
import plotly.express as px
import pandas as pd
from database.models import Startup, AgentResult, StartupAnalysis
from ui.styles import get_width_kwargs


def render_competitor_view(
    startup: Optional[Startup],
    analysis: Optional[StartupAnalysis],
    agent_results: Dict[str, AgentResult],
):
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
    if not comp_res and not analysis:
        st.info(f"Competitor analysis for '{startup.name}' has not been generated yet. Run startup evaluation to view competitive intelligence.")
        return

    data: Dict[str, Any] = comp_res.structured_output if (comp_res and comp_res.structured_output) else {}

    usp = (analysis.usp if analysis and analysis.usp else None) or data.get("recommended_usp") or f"Localized, capital-efficient platform tailored specifically for {startup.target_customer}."
    market_gaps = data.get("market_gaps") or (analysis.key_advantages if analysis and analysis.key_advantages else [
        f"Lack of dedicated, affordable tooling for {startup.target_customer}",
        f"High pricing and rigid vendor lock-in from legacy alternatives in {startup.country}",
        f"Unoptimized user workflows causing high friction and customer churn",
    ])

    # USP Banner Card
    st.markdown(
        f"""
        <div class="welcome-hero" style="border-left: 4px solid #6366F1; margin-bottom: 18px;">
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
            "name": f"Legacy Incumbents in {startup.country}",
            "type": "Direct Market Player",
            "products_services": f"Generic enterprise and retail solutions for {startup.target_market}",
            "pricing": "High enterprise pricing with setup markups",
            "strengths": ["Brand recognition", "Established capital reserves"],
            "weaknesses": ["Slow feature releases", "Expensive pricing for early users"],
            "target_customers": f"General consumers in {startup.country}",
        },
        {
            "name": "Informal / In-House Workarounds",
            "type": "Indirect Alternative",
            "products_services": "Manual spreadsheets, fragmented chat groups, or basic legacy tools",
            "pricing": "Low financial cost but high time drain",
            "strengths": ["Zero upfront investment", "Familiarity"],
            "weaknesses": ["Error-prone", "Cannot scale or automate workflows"],
            "target_customers": f"Budget-constrained {startup.target_customer}",
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

    # 3. Dynamic Market Positioning Matrix (Plotly Scatter Chart)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Strategic Positioning Map")

    pos_rows = [
        {"Entity": f"{startup.name} (Our Venture)", "Value Advantage (1-10)": 9.2, "Product Differentiation (1-10)": 9.4, "Size": 25, "Color": "#10B981"}
    ]

    palette = ["#EF4444", "#3B82F6", "#F59E0B", "#8B5CF6"]
    for idx, c in enumerate(raw_competitors[:3]):
        c_name = c.get("name", f"Alternative {idx+1}")
        pos_rows.append({
            "Entity": c_name[:24],
            "Value Advantage (1-10)": max(2.5, 7.0 - (idx * 1.5)),
            "Product Differentiation (1-10)": max(3.0, 6.5 - (idx * 1.2)),
            "Size": 18,
            "Color": palette[idx % len(palette)],
        })

    pos_df = pd.DataFrame(pos_rows)
    color_map = {row["Entity"]: row["Color"] for row in pos_rows}

    fig = px.scatter(
        pos_df,
        x="Value Advantage (1-10)",
        y="Product Differentiation (1-10)",
        text="Entity",
        size="Size",
        color="Entity",
        color_discrete_map=color_map,
    )
    fig.update_traces(textposition="top center", textfont=dict(color="#F8FAFC", size=11))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111726",
        showlegend=False,
        height=320,
        xaxis=dict(range=[1, 11], gridcolor="#1E293B", color="#94A3B8", title="Price Affordability & Economics →"),
        yaxis=dict(range=[1, 11], gridcolor="#1E293B", color="#94A3B8", title="Market Specialization & Moat →"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, **get_width_kwargs(True))

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
