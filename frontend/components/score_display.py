import streamlit as st


def display_overall_score(data):
    if not data:
        return

    score = data.get("ATS_score", data.get("ats_score", 0))

    st.subheader("ATS Score")
    st.metric(
        "Overall ATS Score",
        round(float(score), 1)
    )


def display_score_breakdown(data):
    if not data:
        return

    component_scores = data.get("component_scores", {}) or {}

    st.subheader("Score Breakdown")

    cols = st.columns(5)

    labels = [
        "Formatting",
        "Keywords",
        "Content",
        "Skill Validation",
        "ATS Compatibility",
    ]

    for col, label in zip(cols, labels):
        key = label.lower().replace(" ", "_")
        value = component_scores.get(key, 0)

        with col:
            st.metric(
                label,
                round(float(value), 1)
            )


def render(data):
    if not data:
        return

    display_overall_score(data)
    display_score_breakdown(data)