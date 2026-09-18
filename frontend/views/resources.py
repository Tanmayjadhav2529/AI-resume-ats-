import streamlit as st


def render():
    st.title("Resume Resources")
    st.write("Helpful ATS and resume-writing tips to improve your application.")

    tips = [
        "Match the job description language closely, but keep the tone natural and truthful.",
        "Lead each bullet with a measurable outcome, such as revenue impact, time saved, or scale improved.",
        "Use simple section headings and keep formatting consistent for ATS parsing.",
        "Highlight both technical tools and business outcomes, especially for product or engineering roles.",
        "Use a clean, readable layout with minimal graphics or tables that ATS parsers may ignore.",
    ]

    for tip in tips:
        st.write(f"- {tip}")

    st.markdown("---")
    st.subheader("Quick resume checklist")
    st.markdown(
        """
        - Add exact skills from the JD
        - Include 3–5 relevant accomplishments
        - Quantify outcomes when possible
        - Remove outdated or irrelevant experience
        - Keep file names and formatting ATS-friendly
        """
    )
