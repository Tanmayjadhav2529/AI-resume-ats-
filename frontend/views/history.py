import streamlit as st

from frontend.services import api_client


def render():
    if not st.session_state.get("access_token"):
        st.warning("Please sign in to view your analysis history.")
        return

    st.title("Analysis History")
    try:
        history = api_client.get_history(st.session_state["access_token"])
    except Exception as exc:
        st.error(str(exc))
        return

    if not history:
        st.info("No previous analyses yet.")
        return

    for item in history:
        analysis_id = item.get("id") or item.get("analysis_id")
        filename = item.get("filename") or item.get("title") or "resume"
        ats_score = item.get("ats_score") or item.get("ATS_score") or "--"
        created_at = item.get("created_at") or item.get("date") or "unknown"

        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            st.write(filename)
        with cols[1]:
            st.write(created_at)
        with cols[2]:
            st.write(f"ATS: {ats_score}")
        with cols[3]:
            if st.button("View", key=f"view-{analysis_id}"):
                st.session_state["analysis_result"] = item.get("analysis_result")
                st.session_state["current_view"] = "scorer"
                st.rerun()
            if st.button("Delete", key=f"delete-{analysis_id}"):
                try:
                    api_client.delete_history_entry(analysis_id, st.session_state["access_token"])
                    st.success("Analysis deleted.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
