import streamlit as st

from frontend.components import detailed_feedback, jd_comparison, score_display, skill_validation
from frontend.services import api_client


def render():
    if not st.session_state.get("access_token"):
        st.warning("Please sign in to use the ATS scorer.")
        return

    st.title("Resume Analyzer")

    uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx", "doc"])
    job_description = st.text_area("Paste job description", height=220, placeholder="Paste the JD here...")
    submit = st.button("Analyze Resume", use_container_width=True)

    if submit:
        if uploaded_file is None:
            st.warning("Please upload a resume first.")
        elif not job_description.strip():
            st.warning("Please paste a job description to compare against.")
        else:
            with st.spinner("Analyzing your resume..."):
                try:
                    result = api_client.analyze_resume(uploaded_file, job_description, st.session_state["access_token"])
                    st.session_state.analysis_result = result
                    st.success("Analysis complete.")
                except Exception as exc:
                    st.session_state.analysis_result = None
                    st.error(str(exc))

    result = st.session_state.get("analysis_result")
    if not result:
        st.info("Submit a resume to see analysis results here.")
        return

    score_display.render(result)
    jd_comparison.render(result)
    skill_validation.render(result)
    detailed_feedback.render(result)

    if result.get("detailed_feedback"):
        try:
            pdf_bytes = api_client.generate_pdf_report(result, st.session_state["access_token"])
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="ats_report.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.error(f"Unable to generate PDF: {exc}")
