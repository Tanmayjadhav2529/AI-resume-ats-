import streamlit as st


def render(data):
    if not data:
        return

    component_scores = data.get("component_scores", {}) or {}
    st.subheader("ATS Score")
    score = data.get("ATS_score", data.get("ats_score", 0))
    st.metric("Overall ATS Score", round(float(score), 1))

    cols = st.columns(5)
    labels = ["Formatting", "Keywords", "Content", "Skill Validation", "ATS Compatibility"]
    for col, label in zip(cols, labels):
        key = label.lower().replace(" ", "_")
        value = component_scores.get(key, 0)
        with col:
            st.metric(label, round(float(value), 1))
