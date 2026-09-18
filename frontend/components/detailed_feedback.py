import streamlit as st


def render(data):
    feedback = data.get("detailed_feedback", []) or []
    if not feedback:
        st.info("No detailed feedback generated.")
        return

    st.subheader("Detailed Feedback")
    for item in feedback:
        title = item.get("issue_title", "Issue")
        severity = item.get("severity_level", "info").upper()
        how_to_fix = item.get("how_to_fix", "Review the item and improve the evidence.")
        with st.expander(f"{title} — {severity}"):
            st.write(how_to_fix)
            explanation = item.get("explanation")
            if explanation:
                st.write(f"Explanation: {explanation}")
