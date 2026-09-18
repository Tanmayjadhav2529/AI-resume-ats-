import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from frontend.services import api_client, supabase_client
from frontend.views import history, landing, resources, scorer

st.set_page_config(
    page_title="AI Resume ATS",
    page_icon="📄",
    layout="wide",
)

with open(Path(__file__).resolve().parent / "assets" / "styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

for key, default in {
    "access_token": None,
    "refresh_token": None,
    "user_id": None,
    "user_email": None,
    "auth_error": "",
    "auth_info": "",
    "current_view": "landing",
    "analysis_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

if "code" in st.query_params and not st.session_state.access_token:
    code = st.query_params["code"]
    result = supabase_client.exchange_code_for_session(code)
    if "error" in result:
        st.session_state.auth_error = result["error"]
    else:
        st.session_state.access_token = result.get("access_token")
        st.session_state.refresh_token = result.get("refresh_token")
        st.session_state.user_id = result.get("user_id")
        st.session_state.user_email = result.get("email")
        st.session_state.auth_info = "Signed in with Google."
        st.session_state.current_view = "scorer"
    st.query_params.clear()
    st.rerun()


def set_view(view_name: str):
    st.session_state.current_view = view_name
    st.rerun()


def sign_out():
    supabase_client.sign_out()
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.auth_error = ""
    st.session_state.auth_info = "Signed out."
    st.session_state.current_view = "landing"
    st.rerun()


with st.sidebar:
    st.title("Navigation")
    for name, label in [("landing", "Home"), ("scorer", "Scorer"), ("history", "History"), ("resources", "Resources")]:
        if st.button(label, use_container_width=True, key=f"nav-{name}"):
            set_view(name)

    st.markdown("---")
    st.subheader("Account")

    if st.session_state.access_token:
        st.write(f"Signed in as: {st.session_state.user_email or 'user'}")
        if st.button("Sign out", use_container_width=True):
            sign_out()
    else:
        sign_in_tab, sign_up_tab = st.tabs(["Sign In", "Sign Up"])

        with sign_in_tab:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Sign in", use_container_width=True):
                if not email or not password:
                    st.session_state.auth_error = "Email and password are required."
                else:
                    result = supabase_client.sign_in_with_password(email, password)
                    if "error" in result:
                        st.session_state.auth_error = result["error"]
                    else:
                        st.session_state.access_token = result.get("access_token")
                        st.session_state.refresh_token = result.get("refresh_token")
                        st.session_state.user_id = result.get("user_id")
                        st.session_state.user_email = result.get("email")
                        st.session_state.auth_error = ""
                        st.session_state.auth_info = "Signed in successfully."
                        st.session_state.current_view = "scorer"
                        st.rerun()

        with sign_up_tab:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Create account", use_container_width=True):
                if not email or not password:
                    st.session_state.auth_error = "Email and password are required."
                else:
                    result = supabase_client.sign_up_with_password(email, password)
                    if result.get("error"):
                        st.session_state.auth_error = result["error"]
                    elif result.get("pending_confirmation"):
                        st.session_state.auth_info = "Account created. Check your email to confirm before signing in."
                        st.session_state.auth_error = ""
                    else:
                        st.session_state.access_token = result.get("access_token")
                        st.session_state.refresh_token = result.get("refresh_token")
                        st.session_state.user_id = result.get("user_id")
                        st.session_state.user_email = result.get("email")
                        st.session_state.auth_info = "Account created successfully."
                        st.session_state.auth_error = ""
                        st.session_state.current_view = "scorer"
                        st.rerun()

        google_url = supabase_client.google_oauth_url()
        if "error" in google_url:
            st.warning(google_url["error"])
        else:
            if st.button("Continue with Google", use_container_width=True):
                st.session_state.auth_error = ""
                st.link_button("Continue with Google", google_url["url"])

    if st.session_state.auth_error:
        st.error(st.session_state.auth_error)
    if st.session_state.auth_info:
        st.success(st.session_state.auth_info)


if st.session_state.current_view == "landing":
    landing.render()
elif st.session_state.current_view == "scorer":
    scorer.render()
elif st.session_state.current_view == "history":
    history.render()
elif st.session_state.current_view == "resources":
    resources.render()
else:
    landing.render()

# Keep backend health info available without blocking the app when auth is not configured yet.
try:
    api_client.health_check()
except Exception:
    pass
