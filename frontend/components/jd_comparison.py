import streamlit as st


def render(data):
    jd = data.get("jd_comparison") or data.get("jd_match_analysis") or {}
    if not jd:
        st.info("No JD comparison data returned.")
        return

    st.subheader("JD Comparison")
    st.metric("Keyword Match", jd.get("match_percentage", 0))
    st.metric("Semantic Similarity", jd.get("semantic_similarity", 0))

    matched = jd.get("matched_keywords", []) or []
    missing = jd.get("missing_keywords", []) or []
    skills_gap = jd.get("skills_gap", []) or []

    if matched:
        st.write("Matched keywords")
        st.markdown(" ".join(f"<span class='keyword-chip'>{k}</span>" for k in matched), unsafe_allow_html=True)
    if missing:
        st.write("Missing keywords")
        st.markdown(" ".join(f"<span class='keyword-chip'>{k}</span>" for k in missing), unsafe_allow_html=True)
    if skills_gap:
        st.write("Skills gap")
        st.markdown("<ul>" + "".join(f"<li>{k}</li>" for k in skills_gap) + "</ul>", unsafe_allow_html=True)
