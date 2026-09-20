from typing import Optional

import requests
import streamlit as st

from frontend.components.dashboard import display_results_dashboard
from frontend.services import api_client


def _read_jd(jd_file, jd_text: str) -> str:
    """Convert the selected JD input into plain text."""

    if jd_text:
        return jd_text.strip()

    if jd_file is None:
        return ""

    if jd_file.name.lower().endswith(".txt"):
        return jd_file.getvalue().decode("utf-8", errors="ignore")

    st.warning(
        "Job description files must be `.txt` for now. "
        "Alternatively, paste the job description text."
    )

    return ""


def _show_backend_error(exc: Exception) -> None:
    """Display a user-friendly backend error."""

    if isinstance(exc, requests.ConnectionError):
        st.error(
            "Could not reach the backend. "
            "Make sure your FastAPI server is running on port 8000."
        )

    elif isinstance(exc, requests.Timeout):
        st.error(
            "The backend took too long to respond. "
            "Please try again."
        )

    elif isinstance(exc, requests.HTTPError) and exc.response is not None:

        try:
            detail = exc.response.json().get(
                "detail",
                exc.response.text,
            )

        except ValueError:
            detail = exc.response.text

        st.error(
            f"Backend returned {exc.response.status_code}: {detail}"
        )

    else:
        st.error(f"Unexpected error: {exc}")


def _summary_text(analysis: dict) -> str:
    """Create a simple downloadable text summary."""

    score = analysis.get(
        "ATS_score",
        analysis.get("ats_score", 0),
    )

    try:
        score = float(score)

    except (TypeError, ValueError):
        score = 0

    lines = [
        f"ATS Score: {score:.0f}/100",
        "",
    ]

    if analysis.get("strengths"):

        lines.append("STRENGTHS:")

        lines.extend(
            f"  - {item}"
            for item in analysis["strengths"]
        )

        lines.append("")

    if analysis.get("critical_issues"):

        lines.append("CRITICAL ISSUES:")

        lines.extend(
            f"  - {item}"
            for item in analysis["critical_issues"]
        )

        lines.append("")

    if analysis.get("suggestions"):

        lines.append("SUGGESTIONS:")

        lines.extend(
            f"  - {item}"
            for item in analysis["suggestions"]
        )

    return "\n".join(lines)


# =============================================================
# UPLOAD AREA
# =============================================================

def _render_upload_area(analysis_mode: str):
    """
    Render the two-column resume/JD input area.

    Returns:
        resume_file, jd_file, jd_text
    """

    left, right = st.columns(2)

    # ---------------------------------------------------------
    # RESUME
    # ---------------------------------------------------------

    with left:

        st.markdown("### 📄 Upload Resume")

        resume_file = st.file_uploader(
            "Choose your resume file",
            type=["pdf", "doc", "docx"],
            help="Supported formats: PDF, DOC, DOCX",
            key="resume_upload",
        )

        if resume_file:

            st.success(
                f"✅ {resume_file.name} "
                f"({resume_file.size / 1024:.1f} KB)"
            )

    # ---------------------------------------------------------
    # JOB DESCRIPTION
    # ---------------------------------------------------------

    jd_file: Optional[object] = None
    jd_text = ""

    with right:

        st.markdown("### 📋 Job Description")

        if analysis_mode == "Job Description Comparison":

            jd_method = st.radio(
                "Input method:",
                [
                    "Paste Text",
                    "Upload .txt File",
                ],
                horizontal=True,
                key="jd_input_method",
            )

            if jd_method == "Upload .txt File":

                jd_file = st.file_uploader(
                    "Choose JD file (.txt only)",
                    type=["txt"],
                    key="jd_upload",
                )

                if jd_file:

                    st.success(
                        f"✅ {jd_file.name}"
                    )

            else:

                jd_text = st.text_area(
                    "Paste job description text:",
                    height=200,
                    placeholder="Paste the JD here...",
                    key="jd_text",
                )

                if jd_text:

                    st.success(
                        f"✅ {len(jd_text)} characters"
                    )

        else:

            st.info(
                "Switch to "
                "**Job Description Comparison** "
                "mode to enable JD matching."
            )

    return resume_file, jd_file, jd_text


# =============================================================
# EXPORT
# =============================================================

def _render_export_buttons(analysis: dict) -> None:
    """Render PDF and TXT export controls."""

    st.markdown("### 📥 Export Results")

    col1, col2 = st.columns(2)

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    with col1:

        if st.button(
            "📑 Generate PDF Report",
            use_container_width=True,
            type="primary",
        ):

            try:

                with st.spinner(
                    "Generating PDF report..."
                ):

                    pdf_bytes = api_client.generate_pdf_report(
                        analysis,
                        st.session_state["access_token"],
                    )

                st.session_state["scorer_pdf_bytes"] = pdf_bytes

            except requests.RequestException as exc:

                _show_backend_error(exc)

            except Exception as exc:

                st.error(
                    f"Unable to generate PDF: {exc}"
                )

        if "scorer_pdf_bytes" in st.session_state:

            st.download_button(
                "⬇️ Download PDF",
                data=st.session_state["scorer_pdf_bytes"],
                file_name="ats_resume_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_report",
            )

    # ---------------------------------------------------------
    # TEXT SUMMARY
    # ---------------------------------------------------------

    with col2:

        st.download_button(
            "📄 Download Summary (.txt)",
            data=_summary_text(analysis),
            file_name="ats_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_summary",
        )


# =============================================================
# MAIN SCORER PAGE
# =============================================================

def render():

    # =========================================================
    # HEADER
    # =========================================================

    # Use st.html instead of st.markdown so the HTML
    # tags are never displayed as literal text.

    st.html(
        """
        <div style="
            text-align:center;
            padding: 1rem 0 0.5rem 0;
        ">

            <h1 style="
                font-size:2.5rem;
                font-weight:700;
                margin:0 0 0.3rem 0;
            ">
                🎯 ATS Resume Scorer
            </h1>

            <p style="
                color:#6B7280;
                font-size:1.05rem;
                margin:0;
            ">
                Upload your resume — and optionally a job
                description — for a comprehensive analysis.
            </p>

        </div>
        """
    )

    # =========================================================
    # SIDEBAR ANALYSIS OPTIONS
    # =========================================================

    with st.sidebar:

        st.markdown("---")

        st.markdown("## 📊 Analysis Options")

        st.info(
            "**General ATS Score**\n\n"
            "Resume only — analyze overall ATS compatibility.\n\n"
            "**JD Comparison**\n\n"
            "Resume + job description — analyze targeted job match."
        )

    # =========================================================
    # ANALYSIS MODE
    # =========================================================

    st.markdown("---")

    analysis_mode = st.radio(
        "Select Analysis Mode:",
        [
            "General ATS Score",
            "Job Description Comparison",
        ],
        horizontal=True,
        key="analysis_mode",
    )

    st.markdown("---")

    # =========================================================
    # UPLOAD SECTION
    # =========================================================

    resume_file, jd_file, jd_text = _render_upload_area(
        analysis_mode
    )

    st.markdown("---")

    # =========================================================
    # NO RESUME
    # =========================================================

    if not resume_file:

        st.info(
            "👆 Upload your resume to begin."
        )

        previous_result = st.session_state.get(
            "analysis_result"
        )

        if previous_result:

            display_results_dashboard(
                previous_result
            )

            _render_export_buttons(
                previous_result
            )

        return

    # =========================================================
    # AUTHENTICATION
    # =========================================================

    access_token = st.session_state.get(
        "access_token"
    )

    if not access_token:

        st.warning(
            "⚠️ Sign in from the sidebar to analyze a resume."
        )

        return

    # =========================================================
    # ANALYZE BUTTON
    # =========================================================

    _, middle, _ = st.columns(
        [1, 2, 1]
    )

    with middle:

        analyze = st.button(
            "🚀 Analyze Resume",
            use_container_width=True,
            type="primary",
        )

    # =========================================================
    # WAITING FOR ANALYSIS
    # =========================================================

    if not analyze:

        previous_result = st.session_state.get(
            "analysis_result"
        )

        if previous_result:

            display_results_dashboard(
                previous_result
            )

            _render_export_buttons(
                previous_result
            )

        return

    # =========================================================
    # CLEAR OLD PDF
    # =========================================================

    st.session_state.pop(
        "scorer_pdf_bytes",
        None,
    )

    # =========================================================
    # JOB DESCRIPTION
    # =========================================================

    if analysis_mode == "Job Description Comparison":

        job_description = _read_jd(
            jd_file,
            jd_text,
        )

        if not job_description:

            st.warning(
                "Please provide a job description "
                "for JD comparison."
            )

            return

    else:

        job_description = ""

    # =========================================================
    # API CALL
    # =========================================================

    try:

        with st.spinner(
            "Analyzing your resume... "
            "This can take 10–30 seconds."
        ):

            # FIX:
            # api_client.analyze_resume() expects
            # `file_obj`, not `resume_file`.

            analysis = api_client.analyze_resume(
                file_obj=resume_file,
                access_token=access_token,
                job_description=job_description,
            )

    except requests.RequestException as exc:

        _show_backend_error(exc)

        return

    except Exception as exc:

        st.error(
            f"Analysis failed: {exc}"
        )

        return

    # =========================================================
    # SAVE RESULT
    # =========================================================

    st.session_state["analysis_result"] = analysis

    st.success(
        "✅ Analysis complete!"
    )

    # =========================================================
    # RESULTS DASHBOARD
    # =========================================================

    display_results_dashboard(
        analysis
    )

    # =========================================================
    # EXPORT
    # =========================================================

    _render_export_buttons(
        analysis
    )