import streamlit as st


def render():
    st.title("AI Resume ATS Analyzer")
    st.subheader("Turn your resume into a recruiter-ready ATS score in minutes.")

    cta, _ = st.columns([1.5, 1])
    with cta:
        if st.button("Start Analyzing Your Resume", use_container_width=True):
            st.session_state.current_view = "scorer"
            st.rerun()

    st.markdown("---")

    st.subheader("Key Features")
    feature_cols = st.columns(4)
    feature_items = [
        ("ATS Scoring", "Get a clear score with recruiter-style feedback."),
        ("Keyword Match", "Compare your resume against the job description."),
        ("Skills Gap", "Spot the missing skills and evidence employers expect."),
        ("Actionable Fixes", "Receive recommendations you can apply immediately."),
    ]
    for col, (title, desc) in zip(feature_cols, feature_items):
        with col:
            st.markdown(f"<div class='card'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("How It Works")
    steps = st.columns(3)
    step_items = [
        ("1. Upload", "Add your resume in PDF or DOCX format."),
        ("2. Analyze", "Compare it against the role and keyword match."),
        ("3. Improve", "Fix weak areas and export a PDF summary."),
    ]
    for col, (title, desc) in zip(steps, step_items):
        with col:
            st.markdown(f"<div class='card'><h4>{title}</h4><p>{desc}</p></div>", unsafe_allow_html=True)
