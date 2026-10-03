"""
AI Co-Founder Chat Screen.
Recreates the chat interface from the UI reference image.
Enables strategic dialogue with the virtual co-founder using startup context and RAG evidence.
"""
from typing import Optional
import streamlit as st
from database.models import Startup
from services.analysis_service import AnalysisService
from ui.styles import get_width_kwargs


def render_chat_view(startup: Optional[Startup]):
    """
    Renders the interactive AI Co-Founder Chat screen.
    """
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin: 0;">
                AI Co-Founder Chat
            </h1>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 4px;">
                Ask questions, debate strategic trade-offs, and receive candid guidance from your virtual executive partner.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not startup:
        st.info("Please create or select a startup to begin chatting with your AI co-founder.")
        return

    c_left, c_right = st.columns([1.1, 2.6], gap="medium")

    # Left Column: Recent Prompts & Shortcuts
    with c_left:
        st.markdown(
            """
            <div style="font-size: 0.82rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 12px;">
                Strategic Discussion Starters
            </div>
            """,
            unsafe_allow_html=True,
        )

        quick_questions = [
            "Why did you say my idea is risky?",
            "What if I charge a monthly subscription?",
            "How do we acquire the first 50 pilot customers?",
            "Compare our pricing with legacy competitors",
            "What should I execute in the next 7 days?",
        ]

        for q in quick_questions:
            if st.button(f"💬 {q}", **get_width_kwargs(True), key=f"quick_{q[:15]}"):
                with st.spinner("AI Co-Founder is thinking..."):
                    AnalysisService.ask_ai_cofounder(startup.id, q)
                st.rerun()

    # Right Column: Chat History & Message Input
    with c_right:
        chat_history = AnalysisService.get_chat_history(startup.id)

        # Chat stream container
        chat_box = st.container(height=420)
        with chat_box:
            if not chat_history:
                st.markdown(
                    f"""
                    <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid #1E293B; border-radius: 12px; padding: 20px; text-align: center; margin-top: 40px;">
                        <div style="font-size: 2rem; margin-bottom: 8px;">🤝</div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">
                            Your AI Co-Founder is ready to help!
                        </div>
                        <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
                            Ask anything regarding customer validation, tech architecture, unit economics, or execution priorities for <b>{startup.name}</b>.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                for msg in chat_history:
                    if msg.sender == "user":
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                                <div style="background: #6366F1; color: #FFFFFF; border-radius: 14px 14px 2px 14px;
                                            padding: 12px 16px; max-width: 80%; font-size: 0.88rem; line-height: 1.4;">
                                    {msg.message}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="display: flex; gap: 10px; margin-bottom: 16px;">
                                <div style="background: #10B981; width: 34px; height: 34px; border-radius: 50%;
                                            display: flex; align-items: center; justify-content: center;
                                            font-size: 1rem; flex-shrink: 0;">
                                    👑
                                </div>
                                <div style="background: #131927; border: 1px solid #1E293B; color: #E2E8F0;
                                            border-radius: 2px 14px 14px 14px; padding: 14px 18px;
                                            max-width: 85%; font-size: 0.88rem; line-height: 1.5;">
                                    <div style="font-size: 0.72rem; color: #10B981; font-weight: 700; margin-bottom: 4px;">
                                        AI CO-FOUNDER (CEO)
                                    </div>
                                    {msg.message}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        # Message Input Form
        with st.form("chat_input_form", clear_on_submit=True):
            user_msg = st.text_input(
                "Type your message...",
                placeholder="Ask about market size, pricing models, tech choices, or execution roadblocks...",
                label_visibility="collapsed",
            )
            submit_chat = st.form_submit_button("Send to Co-Founder →", type="primary", **get_width_kwargs(True))

        if submit_chat and user_msg.strip():
            with st.spinner("AI Co-Founder is analyzing startup context..."):
                AnalysisService.ask_ai_cofounder(startup.id, user_msg.strip())
            st.rerun()
