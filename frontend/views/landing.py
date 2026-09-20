import streamlit as st


def render():

    # =========================================================
    # PAGE CSS
    # =========================================================

    st.markdown(
        """
        <style>
        .main-header {
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(
                135deg,
                #4F46E5 0%,
                #7C3AED 50%,
                #9333EA 100%
            );
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(79, 70, 229, 0.3);
        }

        .main-header h1 {
            font-size: 2.8rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
        }

        .main-header h3 {
            font-size: 1.35rem;
            font-weight: 600;
            margin: 0 0 0.75rem 0;
        }

        .main-header p {
            font-size: 1rem;
            margin: 0;
            opacity: 0.95;
        }

        .feature-card {
            background: #ffffff;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 1.5rem;
            min-height: 220px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        }

        .feature-card h3 {
            color: #1F2937;
            margin-top: 0;
            margin-bottom: 1rem;
        }

        .feature-card p {
            color: #4B5563;
            line-height: 1.6;
        }

        .feature-card li {
            color: #4B5563;
            margin-bottom: 0.45rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================
    # HERO
    # =========================================================

    st.html(
        """
        <div class="main-header">
            <h1>🎯 ATS Resume Scorer</h1>
            <h3>Optimize Your Resume for Applicant Tracking Systems</h3>
            <p>Get instant feedback on your resume's ATS compatibility with AI-powered analysis</p>
        </div>
        """
    )

    # =========================================================
    # CTA
    # =========================================================

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button(
            "🚀 Start Analyzing Your Resume",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.current_view = "scorer"
            st.rerun()

    # =========================================================
    # KEY FEATURES
    # =========================================================

    st.markdown("---")

    st.markdown("## ✨ Key Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.html(
            """
            <div class="feature-card">
                <h3>📊 Comprehensive Scoring</h3>

                <p>
                    Get detailed scores across 5 key dimensions:
                </p>

                <ul>
                    <li>Formatting (20%)</li>
                    <li>Keywords &amp; Skills (25%)</li>
                    <li>Content Quality (25%)</li>
                    <li>Skill Validation (15%)</li>
                    <li>ATS Compatibility (15%)</li>
                </ul>
            </div>
            """
        )

    with col2:
        st.html(
            """
            <div class="feature-card">
                <h3>🔍 Skill Validation</h3>

                <p>
                    Verify that your claimed skills are demonstrated
                    in your projects and experience using AI-powered
                    semantic analysis.
                </p>

                <strong>No more empty claims!</strong>
            </div>
            """
        )

    with col3:
        st.html(
            """
            <div class="feature-card">
                <h3>🔒 Privacy First</h3>

                <p>
                    Your resume is analyzed securely and your
                    results are protected.
                </p>

                <strong>Secure &amp; Private</strong>
            </div>
            """
        )

    # =========================================================
    # HOW IT WORKS
    # =========================================================

    st.markdown("---")

    st.markdown("## 🚀 How It Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.html(
            """
            <div class="feature-card">
                <h3>1️⃣ Upload Your Resume</h3>

                <p>
                    Support for PDF, DOC, and DOCX formats.
                </p>
            </div>
            """
        )

    with col2:
        st.html(
            """
            <div class="feature-card">
                <h3>2️⃣ AI Analysis</h3>

                <p>
                    Our AI models analyze your resume across
                    multiple dimensions.
                </p>
            </div>
            """
        )

    with col3:
        st.html(
            """
            <div class="feature-card">
                <h3>3️⃣ Get Actionable Feedback</h3>

                <p>
                    Receive detailed recommendations to improve
                    your resume.
                </p>
            </div>
            """
        )