"""
Startup Onboarding Form and Creation Flow.
Provides the input form to launch the multi-agent co-founder analysis.
"""
import streamlit as st
from services.startup_service import StartupService
from services.analysis_service import AnalysisService
from utils.constants import (
    COMMON_STARTUP_CATEGORIES,
    COMMON_COUNTRIES,
    FOUNDER_EXPERIENCE_LEVELS,
)
from ui.styles import render_html, get_width_kwargs


def render_startup_form():
    """
    Renders the startup onboarding interface.
    """
    col1, col2 = st.columns([1.1, 1.4], gap="large")

    # Left Column: Hero Branding
    with col1:
        render_html(
            """
            <div class="welcome-hero" style="padding: 40px 24px; text-align: center; border: 1px solid #23304B; height: 100%;">
                <div style="background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(11, 15, 25, 0) 70%);
                            padding: 20px; display: inline-block; border-radius: 50%;">
                    <div style="font-size: 3.5rem;">🚀</div>
                </div>
                <h1 style="color: #FFFFFF; font-size: 2rem; font-weight: 800; margin: 16px 0 8px 0; line-height: 1.2;">
                    Turn Your Idea Into<br><span style="color: #6366F1;">A Real Startup</span>
                </h1>
                <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.5; max-width: 380px; margin: 0 auto 30px auto;">
                    Get AI-powered research, financial modeling, tech architecture, and execution
                    support from your dedicated 6-agent co-founder team.
                </p>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 20px;">
                    <div style="background: #111726; border: 1px solid #1E293B; border-radius: 10px; padding: 12px 6px;">
                        <div style="font-size: 1.4rem;">🔍</div>
                        <div style="font-size: 0.75rem; color: #FFFFFF; font-weight: 600; margin-top: 4px;">Research</div>
                    </div>
                    <div style="background: #111726; border: 1px solid #1E293B; border-radius: 10px; padding: 12px 6px;">
                        <div style="font-size: 1.4rem;">📋</div>
                        <div style="font-size: 0.75rem; color: #FFFFFF; font-weight: 600; margin-top: 4px;">Plan</div>
                    </div>
                    <div style="background: #111726; border: 1px solid #1E293B; border-radius: 10px; padding: 12px 6px;">
                        <div style="font-size: 1.4rem;">💻</div>
                        <div style="font-size: 0.75rem; color: #FFFFFF; font-weight: 600; margin-top: 4px;">Build</div>
                    </div>
                    <div style="background: #111726; border: 1px solid #1E293B; border-radius: 10px; padding: 12px 6px;">
                        <div style="font-size: 1.4rem;">📈</div>
                        <div style="font-size: 0.75rem; color: #FFFFFF; font-weight: 600; margin-top: 4px;">Grow</div>
                    </div>
                </div>
            </div>
            """
        )

    # Right Column: Input Form
    with col2:
        render_html(
            """
            <div style="margin-bottom: 20px;">
                <h2 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0;">
                    Start Your Startup Journey
                </h2>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
                    Tell us about your venture concept and let our AI co-founder team analyze it across every dimension.
                </p>
            </div>
            """
        )

        with st.form("startup_onboarding_form"):
            name = st.text_input(
                "Startup Name *",
                value="CampusBites",
                placeholder="e.g., CampusBites, Solara Health, LogisticsX",
                help="The working brand or company name.",
            )

            idea = st.text_area(
                "Startup Idea *",
                value="AI-powered hyper-local food delivery platform designed specifically for university students, optimizing batch delivery routes and low-cost meal subscriptions.",
                placeholder="Describe the problem, solution, and core offering...",
                height=110,
                help="Clearly specify what your startup does, who it helps, and how it delivers value.",
            )

            c1, c2 = st.columns(2)
            with c1:
                country = st.selectbox(
                    "Operating Country/Region *",
                    options=COMMON_COUNTRIES,
                    index=COMMON_COUNTRIES.index("United States") if "United States" in COMMON_COUNTRIES else 0,
                    help="Country where customer acquisition and legal operations begin.",
                )

            with c2:
                target_market = st.selectbox(
                    "Primary Industry Category *",
                    options=COMMON_STARTUP_CATEGORIES,
                    index=0,
                    help="The primary business category or sector.",
                )

            target_customer = st.text_input(
                "Target Customer Persona *",
                value="University Students (18-25) & Campus Dining Services",
                placeholder="e.g., University students, small clinic doctors, independent restaurants",
                help="Who is the initial paying customer or user base?",
            )

            c3, c4 = st.columns(2)
            with c3:
                budget = st.number_input(
                    "Available Starting Capital ($ USD) *",
                    min_value=500.0,
                    max_value=10_000_000.0,
                    value=25000.0,
                    step=2500.0,
                    help="Your real capital budget for development, legal setup, and initial traction.",
                )

            with c4:
                founder_experience = st.selectbox(
                    "Founder Background & Experience",
                    options=FOUNDER_EXPERIENCE_LEVELS,
                    index=1,
                    help="Helps the CEO calibrate roadmap sprints to your engineering & business capability.",
                )

            additional_context = st.text_area(
                "Special Strategic Constraints or Unfair Advantages (Optional)",
                value="Access to 3 large campus student union partnerships and 12 local restaurants already signed LOIs.",
                placeholder="Any existing distribution advantages, pre-launch signups, regulatory moats...",
                height=70,
            )

            render_html("<div style='height: 10px;'></div>")
            submit_btn = st.form_submit_button("🚀 Build My Startup →", type="primary", **get_width_kwargs(True))

        # 2. Form Submission Handling
        if submit_btn:
            startup, errors = StartupService.create_startup(
                name=name,
                idea=idea,
                country=country,
                target_market=target_market,
                target_customer=target_customer,
                budget=budget,
                currency="$",
                founder_name="Ali Hassan",
                founder_experience=founder_experience,
                additional_context=additional_context,
            )

            if errors:
                for err in errors:
                    st.error(f"Validation error: {err}")
                return

            st.session_state["selected_startup_id"] = startup.id

            # 3. Live Execution Container
            progress_box = st.container()
            with progress_box:
                st.markdown("### 🤖 AI Founding Team In Progress")
                status_text = st.empty()
                progress_bar = st.progress(0.0)

                agent_status_placeholders = {
                    "market_research": st.empty(),
                    "competitor_analysis": st.empty(),
                    "finance": st.empty(),
                    "marketing": st.empty(),
                    "cto": st.empty(),
                    "ceo": st.empty(),
                }

                weights = {
                    "market_research": 0.16,
                    "competitor_analysis": 0.33,
                    "finance": 0.50,
                    "marketing": 0.67,
                    "cto": 0.83,
                    "ceo": 1.0,
                }

                def update_ui(agent_key: str, status: str, msg: str, token_info: dict):
                    pct = weights.get(agent_key, 0.5)
                    progress_bar.progress(pct)
                    status_text.info(f"**{agent_key.replace('_', ' ').title()}**: {msg}")
                    ph = agent_status_placeholders.get(agent_key)
                    if ph:
                        badge_color = "#10B981" if status == "completed" else ("#3B82F6" if status == "running" else "#EF4444")
                        ph.markdown(
                            f"<div style='color: {badge_color}; font-size: 0.85rem;'>● {agent_key.replace('_', ' ').title()}: <b>{status.upper()}</b></div>",
                            unsafe_allow_html=True,
                        )

                with st.spinner("Your 6 specialized AI co-founders are conducting deep venture evaluation..."):
                    try:
                        AnalysisService.run_full_analysis(startup, progress_callback=update_ui)
                        st.success("🎉 Comprehensive Venture Blueprint & Dynamic Roadmap successfully generated!")
                        st.session_state["current_page"] = "Overview"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during agent execution: {str(e)}")
