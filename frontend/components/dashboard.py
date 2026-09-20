from typing import Any, Dict

import streamlit as st

from frontend.components import (
    score_display,
    detailed_feedback,
    jd_comparison,
    skill_validation,
)


def display_strengths(strengths):
    st.markdown("### 💪 Strengths")

    if not strengths:
        st.info("Keep improving your resume to unlock strengths!")
        return

    for item in strengths:
        st.markdown(f"- {item}")


def display_critical_issues(analysis: Dict[str, Any]):
    critical = analysis.get("critical_issues") or []
    summary = analysis.get("issues_summary") or []

    if not critical and not summary:
        st.success("### ✅ No Critical Issues Found!")
        st.markdown(
            "Your resume doesn't have any urgent issues. Nice work."
        )
        return

    st.markdown("### 🚨 Critical Issues")

    st.error(
        "These issues should be addressed first for better ATS performance."
    )

    for item in critical:
        st.markdown(f"- {item}")

    extra = [
        item for item in summary
        if item not in critical
    ]

    if extra:
        with st.expander(
            "📋 Additional flagged items",
            expanded=False,
        ):
            for item in extra:
                st.markdown(f"- {item}")


def display_action_items(analysis: Dict[str, Any]):
    items = []

    for issue in analysis.get("detailed_feedback") or []:

        severity = (
            issue.get("severity_level")
            or issue.get("severity")
            or "low"
        ).lower()

        title = (
            issue.get("issue_title")
            or issue.get("title")
            or "Resume Issue"
        )

        for action in issue.get("action_items") or []:
            items.append(
                (severity, title, action)
            )

    if not items:

        for suggestion in analysis.get("suggestions") or []:
            items.append(
                ("medium", "General", suggestion)
            )

    if not items:
        return

    severity_rank = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    items.sort(
        key=lambda x: severity_rank.get(x[0], 99)
    )

    st.markdown("### ⚡ Action Items")

    st.caption(
        "Concrete steps to improve your score, "
        "sorted by urgency."
    )

    icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }

    for severity, source, action in items:

        icon = icons.get(
            severity,
            "🟢"
        )

        st.markdown(
            f"- {icon} **[{source}]** {action}"
        )


def display_recommendations(analysis: Dict[str, Any]):
    suggestions = analysis.get(
        "suggestions"
    ) or []

    if not suggestions:
        return

    st.markdown("### 💡 Recommendations")

    for suggestion in suggestions:
        st.markdown(
            f"- {suggestion}"
        )


def display_results_dashboard(
    analysis: Dict[str, Any]
):
    """
    Render the complete ATS analysis dashboard.
    """

    # =========================================================
    # OVERALL SCORE
    # =========================================================

    score_display.display_overall_score(
        analysis
    )

    st.markdown("---")

    # =========================================================
    # SCORE BREAKDOWN
    # =========================================================

    score_display.display_score_breakdown(
        analysis
    )

    st.markdown("---")

    # =========================================================
    # STRENGTHS
    # =========================================================

    display_strengths(
        analysis.get("strengths") or []
    )

    st.markdown("---")

    # =========================================================
    # CRITICAL ISSUES
    # =========================================================

    display_critical_issues(
        analysis
    )

    st.markdown("---")

    # =========================================================
    # SKILL VALIDATION
    # =========================================================

    skill_validation.render(
        analysis
    )

    st.markdown("---")

    # =========================================================
    # JD COMPARISON
    # =========================================================

    jd_data = (
        analysis.get("jd_comparison")
        or analysis.get("jd_match_analysis")
    )

    if jd_data:

        jd_comparison.render(
            jd_data
        )

        st.markdown("---")

    # =========================================================
    # DETAILED FEEDBACK
    # =========================================================

    detailed_feedback.render(
        analysis
    )

    st.markdown("---")

    # =========================================================
    # ACTION ITEMS
    # =========================================================

    display_action_items(
        analysis
    )

    st.markdown("---")

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    display_recommendations(
        analysis
    )