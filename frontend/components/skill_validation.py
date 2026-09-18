import streamlit as st


def render(data):
    validation = data.get("skill_validation_details") or {}
    if not validation:
        st.info("No skill validation data found.")
        return

    st.subheader("Skill Validation")
    validated = validation.get("validated", []) or []
    unvalidated = validation.get("unvalidated", []) or []
    total = validation.get("total", 0)
    pct = validation.get("validation_pct", 0)

    st.metric("Validated Skills", f"{validation.get('validated_count', len(validated))}/{total or len(validated)}")
    st.metric("Validation %", f"{pct}%")

    if validated:
        with st.expander("Validated skills"):
            for item in validated:
                st.write(item)
    if unvalidated:
        with st.expander("Unvalidated skills"):
            for item in unvalidated:
                st.write(f"- {item}")
