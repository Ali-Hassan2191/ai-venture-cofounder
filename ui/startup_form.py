"""
Startup Onboarding Form Screen.
Recreates the onboarding journey screen from the UI reference image.
Triggers live multi-agent CrewAI execution upon submission.
"""
from typing import Optional
import streamlit as st
from database.models import Startup
from services.startup_service import StartupService
from services.analysis_service import AnalysisService
from config.llm_config import global_token_manager, get_llm_config


def render_startup_form():
    """
    Renders the startup onboarding interface.
    """
    col1, col2 = st.columns([1.1, 1.4], gap="large")

    # Left Column: Hero Branding
    with col1:
        st.markdown(
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
            """,
            unsafe_allow_html=True,
        )

    # Right Column: Input Form
    with col2:
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h2 style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0;">
                    Start Your Startup Journey
                </h2>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
                    Tell us about your venture concept and let our AI co-founder team analyze it across every dimension.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
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
                help="A clear summary of the customer problem and how your solution solves it.",
            )

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                country = st.text_input(
                    "Operating Country / Region *",
                    value="United States",
                    placeholder="e.g. United States, United Kingdom, Pakistan, Germany",
                )
            with f_col2:
                target_customer = st.text_input(
                    "Target Customer *",
                    value="University Students (18-25 years)",
                    placeholder="e.g. B2B Sales Teams, University Students, Freelancers",
                )

            b_col1, b_col2 = st.columns(2)
            with b_col1:
                budget = st.number_input(
                    "Initial Capital Budget ($) *",
                    min_value=500.0,
                    max_value=10_000_000.0,
                    value=25000.0,
                    step=1000.0,
                    format="%.0f",
                )
            with b_col2:
                founder_experience = st.selectbox(
                    "Founder Experience *",
                    options=["Beginner", "Intermediate", "Experienced Serial Founder", "Domain Expert"],
                    index=0,
                )

            additional_context = st.text_input(
                "Additional Strategic Context (Optional)",
                value="Access to 3 large campus student networks and 15 partner food vendors willing to pilot.",
                placeholder="e.g., Partnerships, unfair advantages, existing domain connections...",
            )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("🚀 Build My Startup →", type="primary", use_container_width=True)

        if submit_btn:
            # 1. Validate credentials check
            cfg = get_llm_config()
            if not cfg.get("api_key"):
                st.error(
                    "⚠️ Groq API key is missing. Please configure `GROQ_API_KEY` in `.streamlit/secrets.toml` "
                    "or in your Streamlit Cloud App Secrets settings."
                )
                return

            # 2. Validate inputs & persist startup
            startup, errors = StartupService.create_startup(
                name=name,
                idea=idea,
                country=country,
                target_market=f"{country} - {target_customer}",
                target_customer=target_customer,
                budget=budget,
                currency="$",
                founder_name="Founder",
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
