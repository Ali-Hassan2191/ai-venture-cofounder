"""
AI Venture Co-Founder - Main Application Entrypoint.
Production-ready Streamlit interface for venture analysis, dynamic execution roadmaps, and co-founder intelligence.
Compatible with Python 3.12, Streamlit Community Cloud, and Groq.
"""
import sys
import os

# Ensure current directory is on sys.path for clean module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="AI Venture Co-Founder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.constants import APP_NAME
from database.database import init_db
from database.repository import StartupRepository
from database.models import Startup, StartupAnalysis, DynamicRoadmap, RoadmapTask
from services.startup_service import StartupService
from services.analysis_service import AnalysisService
from services.roadmap_service import RoadmapService
from config.llm_config import get_llm_config, global_token_manager
from rag.faiss_manager import faiss_manager
from ui import (
    apply_theme,
    render_sidebar,
    render_dashboard,
    render_startup_form,
    render_agents_view,
    render_market_view,
    render_competitor_view,
    render_finance_view,
    render_blueprint_view,
    render_execution_view,
    render_progress_view,
    render_chat_view,
    render_reports_view,
)


def seed_default_venture_if_empty():
    """
    Seeds a realistic initial startup venture if the database is newly initialized,
    enabling the user to explore the dashboard, blueprint, and dynamic roadmap immediately.
    """
    existing = StartupRepository.list_startups()
    if existing:
        return

    # Seed initial realistic venture
    startup = Startup(
        name="CampusBites AI",
        idea=(
            "AI-powered hyper-local food delivery platform designed specifically for university students, "
            "optimizing batch dorm delivery routes, scheduled lunch drops, and affordable student meal subscriptions."
        ),
        country="United States",
        target_market="University Students (18-25)",
        target_customer="University Students & Campus Vendors",
        budget=25000.0,
        currency="$",
        founder_name="Ahmed Khan",
        founder_experience="Intermediate",
        additional_context="Access to 3 large campus student networks and 15 partner food vendors.",
        status="completed",
    )
    s_id = StartupRepository.create_startup(startup)
    startup.id = s_id

    # Seed analysis
    analysis = StartupAnalysis(
        startup_id=s_id,
        overall_score=76,
        category_scores={
            "market": 82,
            "competition": 64,
            "business_model": 73,
            "finance": 68,
            "technology": 91,
            "risk": 59,
        },
        difficulty_level="MEDIUM",
        difficulty_reasoning=(
            "Moderate operational complexity in courier batching balanced by high customer density, "
            "standard technical scope, and strong local network effects."
        ),
        executive_summary=(
            "CampusBites AI is an AI-powered food delivery platform designed specifically for university "
            "students. The platform focuses on affordable, fast, and scheduled delivery within university "
            "campuses, addressing the unique needs of students with budget-friendly pricing, dorm drop coordination, "
            "and batch dispatch efficiency."
        ),
        problem_statement="Existing delivery apps charge $5-8 in fees and have unpredictable delivery times across dorms.",
        solution_statement="Scheduled campus batch runs and vendor partnerships delivering meals under $10 total.",
        usp="Batch delivery routing designed specifically for multi-building university dorm complexes.",
        business_model="Commission on vendor orders (15%) + $1.49 batch delivery fee + Student Saver subscription.",
        revenue_model="Multi-tiered: Order commission, subscription membership ($9.99/mo), and campus vendor promotions.",
        core_features=[
            "Feature 1: Campus Meal Batch Ordering",
            "Feature 2: Dorm Drop Location Coordinator",
            "Feature 3: Frictionless Student Payment & Split Billing",
            "Feature 4: Vendor Prep & Dispatch Portal",
        ],
        technical_direction="Streamlit responsive UI, Python backend services, SQLite persistence, and vector RAG retrieval.",
        financial_overview="Unit economics become profitable at 450 monthly orders; initial runway estimated at 8 months.",
        key_advantages=[
            "Campus-focused delivery model with extreme drop-off density",
            "High daily repeat demand for affordable food options",
            "Initial product build executable within 4-6 weeks",
            "Estimated break-even: 1,500 orders/month",
        ],
        major_risks=[
            "High customer acquisition cost outside peak campus semesters",
            "Vendor fulfillment delays during concentrated lunch rush hours",
        ],
        risk_analysis={
            "market_risk": {"description": "Summer break demand dip", "impact": "Medium", "reason": "Students off campus", "mitigation": "Partner with summer programs & local hospital clusters"},
            "financial_risk": {"description": "Courier wage inflation", "impact": "Medium", "reason": "Student courier turnover", "mitigation": "Peer student courier incentive model"},
            "technical_risk": {"description": "Peak hour order latency", "impact": "Low", "reason": "Spikes at 12pm & 6pm", "mitigation": "Asynchronous order queue and pre-order batches"},
            "competition_risk": {"description": "Legacy app promotions", "impact": "Medium", "reason": "Deep pocket incumbents", "mitigation": "Lock-in student dorm ambassador exclusivity"},
        },
        recommended_next_steps=[
            "Run Day 5 pricing validation with 10 student focus groups",
            "Sign initial LOIs with 5 campus-adjacent food vendors",
            "Finalize batch route dispatch algorithm",
            "Deploy closed alpha on primary campus for 100 students",
        ],
        feasibility_verdict="Good Potential",
    )
    StartupRepository.save_analysis(analysis)

    # Seed dynamic 45-day roadmap (Not fixed 30 days)
    dynamic_tasks = [
        RoadmapTask(0, 1, "Validation Phase", "Define customer interview script & student personas", is_completed=True),
        RoadmapTask(0, 2, "Validation Phase", "Survey 50 students on delivery fee pain thresholds", is_completed=True),
        RoadmapTask(0, 3, "Validation Phase", "Interview 5 local restaurant managers on commission openness", is_completed=True),
        RoadmapTask(0, 4, "Validation Phase", "Analyze user interview results & fee sensitivity", is_completed=True),
        RoadmapTask(0, 5, "Validation Phase", "Pricing Validation - Test different student pricing models with 10 users", is_completed=False, milestone_tag="Pricing Gate"),
        RoadmapTask(0, 10, "Validation Phase", "Formalize Customer Validation Sign-off", is_completed=False, milestone_tag="Validation Milestone"),
        RoadmapTask(0, 15, "Core Build Phase", "Setup Database Schema & Service Architecture", is_completed=False),
        RoadmapTask(0, 25, "Core Build Phase", "Implement Real-time Dorm Drop Batch Routing Engine", is_completed=False, milestone_tag="Core Architecture Complete"),
        RoadmapTask(0, 35, "Pilot Phase", "Launch Closed Alpha with 50 Pilot Students", is_completed=False, milestone_tag="Alpha Milestone"),
        RoadmapTask(0, 45, "Launch Phase", "Campus Public Launch & First 250 Paying Customers", is_completed=False, milestone_tag="Public Launch Milestone"),
    ]

    roadmap = DynamicRoadmap(
        startup_id=s_id,
        total_duration_days=45,
        current_day=4,
        current_phase="Validation Phase",
        progress_percent=40.0,
        milestones=[
            {"day": 5, "title": "Pricing Model Sign-off"},
            {"day": 10, "title": "Customer Problem Validation"},
            {"day": 25, "title": "Core Build Complete"},
            {"day": 35, "title": "Closed Alpha Sign-off"},
            {"day": 45, "title": "Public Launch"},
        ],
        tasks=dynamic_tasks,
    )
    StartupRepository.save_roadmap(roadmap)


def render_settings_view():
    """Renders environment, LLM, and RAG configuration diagnostics."""
    st.markdown("## ⚙️ Platform & Provider Settings")

    cfg = get_llm_config()
    st.markdown("### LLM Configuration")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("LLM Provider", cfg["provider"].upper())
    with c2:
        st.metric("Model ID", cfg["model"])
    with c3:
        has_key = bool(cfg["api_key"])
        st.metric("API Key Configured", "✅ Yes" if has_key else "❌ Missing")

    st.markdown("---")
    st.markdown("### Vector RAG Status (FAISS)")
    status = faiss_manager.get_status()
    f1, f2, f3 = st.columns(3)
    with f1:
        st.metric("Index Loaded", "✅ Active" if status["is_loaded"] else "⚠️ Offline")
    with f2:
        st.metric("Vector Dimension", status["dimension"])
    with f3:
        st.metric("Total Indexed Records", status["metadata_count"])

    if not status["is_loaded"]:
        st.warning(f"FAISS Status: {status['load_error']}")

    st.markdown("---")
    st.markdown("### Global Token Budget Manager")
    b_summary = global_token_manager.get_summary()
    st.json(b_summary)


def main():
    # 1. Initialize SQLite Database & Theme
    init_db()
    apply_theme()
    seed_default_venture_if_empty()

    # 2. Load Startups
    startups = StartupService.list_all_startups()

    selected_id = st.session_state.get("selected_startup_id")
    active_startup = None

    if selected_id:
        active_startup = StartupService.get_startup(selected_id)

    if not active_startup and startups:
        active_startup = startups[0]
        st.session_state["selected_startup_id"] = active_startup.id

    # 3. Load Active Analysis, Roadmap, and Agent Results
    analysis = None
    roadmap = None
    agent_results = {}

    if active_startup:
        analysis = AnalysisService.get_analysis_for_startup(active_startup.id)
        roadmap = RoadmapService.get_roadmap_for_startup(active_startup.id)
        agent_results = AnalysisService.get_agent_results(active_startup.id)

    # 4. Render Sidebar Navigation
    current_page = render_sidebar(startups, active_startup)

    # 5. Route to Active Screen
    if current_page == "Overview":
        render_dashboard(active_startup, analysis, roadmap, agent_results)
    elif current_page == "Startup Idea":
        render_startup_form()
    elif current_page == "AI Agents":
        render_agents_view(active_startup, agent_results)
    elif current_page == "Market Analysis":
        render_market_view(active_startup, agent_results)
    elif current_page == "Competitors":
        render_competitor_view(active_startup, agent_results)
    elif current_page == "Financial Model":
        render_finance_view(active_startup, agent_results)
    elif current_page == "Blueprint":
        render_blueprint_view(active_startup, analysis, roadmap)
    elif current_page == "Execution Plan":
        render_execution_view(active_startup, roadmap)
    elif current_page == "Progress":
        render_progress_view(active_startup, roadmap, agent_results)
    elif current_page == "Chat":
        render_chat_view(active_startup)
    elif current_page == "Reports":
        render_reports_view(active_startup, analysis, roadmap)
    elif current_page == "Settings":
        render_settings_view()
    else:
        render_dashboard(active_startup, analysis, roadmap, agent_results)


if __name__ == "__main__":
    main()
