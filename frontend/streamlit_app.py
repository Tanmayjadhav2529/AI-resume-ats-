import os
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="AI Resume ATS",
    page_icon="📄",
    layout="wide",
)

with open(Path(__file__).resolve().parent / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("AI Resume ATS Analyzer")
st.caption("Upload your resume and compare it against a job description in real time.")

with st.container():
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "doc"])
        job_description = st.text_area(
            "Paste job description",
            height=220,
            placeholder="Paste the JD here...")
        submit = st.button("Analyze Resume", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Quick stats")
        st.metric("ATS Score", "--")
        st.metric("Keyword Match", "--")
        st.metric("Skills Gap", "--")
        st.markdown('</div>', unsafe_allow_html=True)

if submit:
    if uploaded_file is None:
        st.warning("Please upload a resume first.")
    elif not job_description.strip():
        st.warning("Please paste a job description to compare against.")
    else:
        with st.spinner("Analyzing your resume..."):
            st.success("Frontend ready. Connect this form to the backend API to fetch live analysis.")
            st.code(
                {
                    "file": uploaded_file.name,
                    "job_description_length": len(job_description),
                    "status": "waiting_for_backend",
                },
                language="json",
            )

st.markdown("---")

left, center, right = st.columns(3)
with left:
    st.markdown('<div class="metric-box"><h4>Skill Coverage</h4><p>--</p></div>', unsafe_allow_html=True)
with center:
    st.markdown('<div class="metric-box"><h4>Experience Match</h4><p>--</p></div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="metric-box"><h4>Improvement Score</h4><p>--</p></div>', unsafe_allow_html=True)

st.subheader("Issues found")
for i in range(3):
    st.markdown(
        '<div class="issue-box"><strong>Issue #1</strong><br>Missing project evidence or keyword alignment.</div>',
        unsafe_allow_html=True,
    )

st.subheader("Matched keywords")
for tag in ["Python", "FastAPI", "SQL", "Machine Learning", "React"]:
    st.markdown(f'<span class="keyword-chip">{tag}</span>', unsafe_allow_html=True)
