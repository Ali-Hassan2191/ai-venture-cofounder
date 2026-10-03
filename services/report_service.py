"""
PDF Report Generation Service using ReportLab.
Generates an executive-ready Venture Blueprint & Evaluation Dossier.
"""
import os
import io
import logging
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

from database.models import Startup, StartupAnalysis, DynamicRoadmap
from database.repository import StartupRepository

logger = logging.getLogger(__name__)


class ReportService:

    @staticmethod
    def generate_startup_pdf(
        startup: Startup,
        analysis: Optional[StartupAnalysis] = None,
        roadmap: Optional[DynamicRoadmap] = None,
    ) -> bytes:
        """
        Builds a comprehensive, publication-grade PDF report.
        Returns the PDF as raw bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Custom professional styles
        primary_color = colors.HexColor("#4F46E5")  # Indigo
        dark_bg = colors.HexColor("#0F172A")
        text_dark = colors.HexColor("#1E293B")
        slate_gray = colors.HexColor("#64748B")
        emerald = colors.HexColor("#059669")
        amber = colors.HexColor("#D97706")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=4,
        )

        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=slate_gray,
            spaceAfter=15,
        )

        h1_style = ParagraphStyle(
            "Heading1_Custom",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "Body_Custom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=text_dark,
            spaceAfter=6,
        )

        bold_label = ParagraphStyle(
            "BoldLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("AI VENTURE CO-FOUNDER", title_style))
        story.append(
            Paragraph(
                f"Official Venture Blueprint & Executive Assessment Dossier | {startup.name}",
                subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

        # 2. Startup Overview Meta Table
        score_val = analysis.overall_score if analysis else 75
        verdict_val = analysis.feasibility_verdict if analysis else "Good Potential"
        duration_val = f"{roadmap.total_duration_days} Days" if roadmap else "Dynamic Duration"

        meta_data = [
            [
                Paragraph("<b>Startup Name:</b>", bold_label),
                Paragraph(startup.name, body_style),
                Paragraph("<b>Overall Score:</b>", bold_label),
                Paragraph(f"<font color='{emerald.hexval()}'><b>{score_val}/100</b></font>", body_style),
            ],
            [
                Paragraph("<b>Operating Market:</b>", bold_label),
                Paragraph(f"{startup.target_market} ({startup.country})", body_style),
                Paragraph("<b>Feasibility Verdict:</b>", bold_label),
                Paragraph(f"<b>{verdict_val}</b>", body_style),
            ],
            [
                Paragraph("<b>Target Customer:</b>", bold_label),
                Paragraph(startup.target_customer, body_style),
                Paragraph("<b>Execution Duration:</b>", bold_label),
                Paragraph(duration_val, body_style),
            ],
            [
                Paragraph("<b>Available Budget:</b>", bold_label),
                Paragraph(f"{startup.currency}{startup.budget:,.2f}", body_style),
                Paragraph("<b>Founder Experience:</b>", bold_label),
                Paragraph(startup.founder_experience, body_style),
            ],
        ]

        meta_table = Table(meta_data, colWidths=[110, 160, 110, 150])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(meta_table)
        story.append(Spacer(1, 12))

        # 3. Executive Summary
        story.append(Paragraph("1. Executive Summary & Opportunity Overview", h1_style))
        exec_text = (
            analysis.executive_summary
            if (analysis and analysis.executive_summary)
            else f"{startup.name} is a high-potential startup venture focused on {startup.target_market}."
        )
        story.append(Paragraph(exec_text, body_style))
        story.append(Spacer(1, 8))

        # 4. Problem & Solution
        story.append(Paragraph("2. Problem & Proposed Value Proposition", h1_style))
        prob_text = analysis.problem_statement if (analysis and analysis.problem_statement) else startup.idea
        sol_text = analysis.solution_statement if (analysis and analysis.solution_statement) else startup.idea
        story.append(Paragraph(f"<b>Problem Statement:</b> {prob_text}", body_style))
        story.append(Paragraph(f"<b>Solution Statement:</b> {sol_text}", body_style))
        if analysis and analysis.usp:
            story.append(Paragraph(f"<b>Unique Selling Proposition (USP):</b> {analysis.usp}", body_style))
        story.append(Spacer(1, 8))

        # 5. Category Scores Breakdown
        if analysis and analysis.category_scores:
            story.append(Paragraph("3. Category Feasibility Scorecard", h1_style))
            cat_data = [["Evaluation Category", "Score (0-100)", "Rating"]]
            for cat, sc in analysis.category_scores.items():
                label = "Strong" if sc >= 80 else ("Moderate" if sc >= 65 else "Risk Area")
                cat_data.append([cat.replace("_", " ").title(), f"{sc}/100", label])

            cat_table = Table(cat_data, colWidths=[200, 150, 180])
            cat_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (1, -1), "CENTER"),
                    ("ALIGN", (2, 0), (2, -1), "CENTER"),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ])
            )
            story.append(cat_table)
            story.append(Spacer(1, 10))

        # 6. Business & Revenue Model
        story.append(Paragraph("4. Business & Revenue Model", h1_style))
        bm_text = analysis.business_model if (analysis and analysis.business_model) else "Direct customer engagement."
        rm_text = analysis.revenue_model if (analysis and analysis.revenue_model) else "Usage and tiered subscriptions."
        story.append(Paragraph(f"<b>Business Operating Model:</b> {bm_text}", body_style))
        story.append(Paragraph(f"<b>Revenue Mechanics:</b> {rm_text}", body_style))
        story.append(Spacer(1, 8))

        # 7. Core Features & Technical Direction
        story.append(Paragraph("5. Core Product Features & Technical Architecture", h1_style))
        if analysis and analysis.core_features:
            for feat in analysis.core_features:
                story.append(Paragraph(f"• {feat}", body_style))
        if analysis and analysis.technical_direction:
            story.append(Paragraph(f"<b>Technical Stack & Direction:</b> {analysis.technical_direction}", body_style))
        story.append(Spacer(1, 8))

        # 8. Multi-Dimensional Risk Analysis
        if analysis and analysis.risk_analysis:
            story.append(Paragraph("6. Multi-Dimensional Risk Analysis", h1_style))
            risk_rows = [["Risk Category", "Impact", "Description", "Mitigation Strategy"]]
            for r_key, r_info in analysis.risk_analysis.items():
                if isinstance(r_info, dict):
                    name_str = r_key.replace("_", " ").title()
                    impact_str = r_info.get("impact", "Medium")
                    desc_str = r_info.get("description", "")
                    mit_str = r_info.get("mitigation", "")
                    risk_rows.append([
                        Paragraph(name_str, bold_label),
                        Paragraph(impact_str, body_style),
                        Paragraph(desc_str[:120], body_style),
                        Paragraph(mit_str[:140], body_style),
                    ])

            if len(risk_rows) > 1:
                r_table = Table(risk_rows, colWidths=[90, 50, 190, 200])
                r_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ])
                )
                story.append(r_table)
                story.append(Spacer(1, 10))

        # 9. Dynamic Execution Roadmap
        if roadmap:
            story.append(Paragraph(f"7. Dynamic Execution Roadmap ({roadmap.total_duration_days} Days)", h1_style))
            story.append(
                Paragraph(
                    f"Roadmap calibrated to technical complexity, market risks, and capital runway. "
                    f"Current Phase: <b>{roadmap.current_phase}</b> | Progress: <b>{roadmap.progress_percent:.1f}%</b>",
                    body_style,
                )
            )

            # Phased Milestone Summary
            if roadmap.milestones:
                m_text = ", ".join([f"Day {m.get('day')}: {m.get('title')}" for m in roadmap.milestones])
                story.append(Paragraph(f"<b>Key Milestones:</b> {m_text}", body_style))

            task_rows = [["Day", "Phase", "Execution Task", "Status"]]
            for t in roadmap.tasks[:12]:  # Show top key tasks in report
                status_label = "DONE" if t.is_completed else "PENDING"
                task_rows.append([
                    f"Day {t.day_number}",
                    t.phase,
                    t.title,
                    status_label,
                ])

            t_table = Table(task_rows, colWidths=[50, 150, 260, 70])
            t_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ])
            )
            story.append(t_table)
            story.append(Spacer(1, 10))

        # 10. Recommended Next Steps & CEO Closing Assessment
        story.append(Paragraph("8. Lead Co-Founder Assessment & Next Steps", h1_style))
        if analysis and analysis.recommended_next_steps:
            for step in analysis.recommended_next_steps:
                story.append(Paragraph(f"✓ {step}", body_style))

        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
        story.append(
            Paragraph(
                "Generated by AI Venture Co-Founder | Strictly Confidential & Proprietary",
                ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=slate_gray, alignment=1),
            )
        )

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Save to reports directory if startup id exists
        try:
            reports_dir = "data/reports"
            os.makedirs(reports_dir, exist_ok=True)
            report_file = os.path.join(reports_dir, f"startup_{startup.id}_blueprint.pdf")
            with open(report_file, "wb") as f:
                f.write(pdf_bytes)
        except Exception as e:
            logger.warning(f"Could not write PDF to filesystem: {e}")

        return pdf_bytes
