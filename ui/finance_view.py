"""
Financial Model Screen.
Displays initial capital requirements, operating costs, revenue projections,
unit economics, and break-even milestones powered by Pandas and Plotly.
"""
from typing import Optional, Dict, Any
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from database.models import Startup, AgentResult
from services.financial_service import FinancialService


def render_finance_view(startup: Optional[Startup], agent_results: Dict[str, AgentResult]):
    """
    Renders the Financial Model screen.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                Financial Model & Unit Economics
            </h1>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                Initial capital deployment, operating burn, pricing tiers, and break-even trajectory.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not startup:
        st.info("Please create or select a startup to view financial model.")
        return

    fin_res = agent_results.get("finance")
    data: Dict[str, Any] = fin_res.structured_output if (fin_res and fin_res.structured_output) else {}

    currency = data.get("currency") or startup.currency or "$"
    dev_cost = float(data.get("development_costs", 12000))
    monthly_ops = float(data.get("monthly_operating_costs", 1800))
    monthly_mkt = float(data.get("monthly_marketing_costs", 1500))
    break_even_str = str(data.get("break_even_point", "450 active subscribers or 1,200 orders/month"))
    revenue_model = data.get("revenue_model", "SaaS Subscriptions + Transaction Platform Fee")

    # 1. Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Initial Dev Investment</div>
                <div class="stat-value" style="color: #F8FAFC;">{currency}{dev_cost:,.0f}</div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Software & Architecture</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Monthly Operating Burn</div>
                <div class="stat-value" style="color: #F59E0B;">{currency}{monthly_ops:,.0f}</div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Hosting & Ops overhead</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Monthly Acquisition Burn</div>
                <div class="stat-value" style="color: #8B5CF6;">{currency}{monthly_mkt:,.0f}</div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Growth & Referral seeding</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        runway = int(startup.budget / (monthly_ops + monthly_mkt + 1e-9)) if startup.budget > 0 else 6
        st.markdown(
            f"""
            <div class="venture-card">
                <div class="stat-label">Capital Runway</div>
                <div class="stat-value" style="color: #10B981;">{runway} <span style="font-size: 1rem; color: #64748B;">Mo</span></div>
                <div style="color: #94A3B8; font-size: 0.75rem; margin-top: 4px;">Based on {currency}{startup.budget:,.0f} budget</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. 12-Month Cashflow Forecast (Pandas & Plotly)
    st.markdown("### 📈 12-Month Revenue & Cashflow Trajectory")
    cashflow_df = FinancialService.calculate_12_month_cashflow(
        initial_budget=startup.budget,
        monthly_fixed_costs=monthly_ops,
        monthly_marketing=monthly_mkt,
        avg_revenue_per_user=19.99,
        expected_monthly_growth_rate=0.20,
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cashflow_df["Month"],
        y=cashflow_df["Revenue"],
        name="Projected Revenue",
        marker_color="#10B981",
    ))
    fig.add_trace(go.Bar(
        x=cashflow_df["Month"],
        y=cashflow_df["Operating Costs"],
        name="Total Monthly Burn",
        marker_color="#EF4444",
    ))
    fig.add_trace(go.Scatter(
        x=cashflow_df["Month"],
        y=cashflow_df["Treasury Balance"],
        name="Treasury Cash Balance",
        yaxis="y2",
        line=dict(color="#6366F1", width=3, dash="dot"),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111726",
        barmode="group",
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#F8FAFC")),
        xaxis=dict(gridcolor="#1E293B", color="#94A3B8"),
        yaxis=dict(gridcolor="#1E293B", color="#94A3B8", title=f"Monthly Amount ({currency})"),
        yaxis2=dict(overlaying="y", side="right", color="#6366F1", title=f"Treasury Balance ({currency})", showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 3. Capital Allocation & Break-Even Metrics Row
    c_col1, c_col2 = st.columns([1.2, 1])

    with c_col1:
        st.markdown("### 🥧 Initial Capital Allocation Breakdown")
        cost_df = FinancialService.build_cost_breakdown_df(
            dev_cost=dev_cost,
            marketing_cost=monthly_mkt * 3,
            ops_cost=monthly_ops * 3,
            reserve_cost=max(2000.0, startup.budget - (dev_cost + (monthly_mkt * 3) + (monthly_ops * 3))),
        )
        pie_fig = px.pie(
            cost_df,
            names="Category",
            values="Amount",
            hole=0.55,
            color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B", "#3B82F6"],
        )
        pie_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(font=dict(color="#F8FAFC", size=10)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
        )
        st.plotly_chart(pie_fig, use_container_width=True)

    with c_col2:
        st.markdown("### 🎯 Break-Even Economics")
        st.markdown(
            f"""
            <div class="welcome-hero" style="padding: 20px;">
                <div style="font-size: 0.8rem; color: #10B981; font-weight: 700; text-transform: uppercase;">
                    Target Break-Even Point
                </div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 6px;">
                    {break_even_str}
                </div>
                <div style="margin-top: 14px; font-size: 0.82rem; color: #94A3B8;">
                    <b>Primary Revenue Model:</b><br>{revenue_model}
                </div>
                <div style="margin-top: 10px; font-size: 0.82rem; color: #94A3B8;">
                    <b>Estimated Gross Margin:</b><br><span style="color: #10B981; font-weight: 700;">68% - 78%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 4. Pricing Options
    pricing_list = data.get("pricing_options") or [
        {"tier_name": "Free Campus Pass", "price": 0.0, "billing_period": "forever", "target_persona": "Casual exploratory user"},
        {"tier_name": "Student Saver Monthly", "price": 14.99, "billing_period": "monthly", "target_persona": "Active student diner"},
        {"tier_name": "Unlimited Dorm Club", "price": 29.99, "billing_period": "monthly", "target_persona": "Power user with zero delivery fees"},
    ]

    st.markdown("### 🏷️ Recommended Pricing Tiers")
    p_cols = st.columns(len(pricing_list))
    for col, tier in zip(p_cols, pricing_list):
        t_name = tier.get("tier_name", "Tier")
        t_price = tier.get("price", 0)
        t_period = tier.get("billing_period", "monthly")
        t_persona = tier.get("target_persona", "Target user")

        with col:
            st.markdown(
                f"""
                <div class="venture-card" style="text-align: center;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">{t_name}</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #6366F1;">
                        {currency}{t_price} <span style="font-size: 0.75rem; color: #64748B;">/{t_period}</span>
                    </div>
                    <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 8px;">
                        {t_persona}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
