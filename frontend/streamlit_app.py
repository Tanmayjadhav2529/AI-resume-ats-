import streamlit as st
import sys
from pathlib import Path

# Make project root importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.services import supabase_client

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="ATS Resume Scorer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

defaults = {
    "access_token": None,
    "refresh_token": None,
    "user_id": None,
    "user_email": None,
    "auth_error": None,
    "auth_info": None,
    "current_view": "landing",
    "analysis_result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# GOOGLE OAUTH CALLBACK
# ---------------------------------------------------------

if (
    not st.session_state.access_token
    and "code" in st.query_params
):

    code = st.query_params["code"]

    result = supabase_client.exchange_code_for_session(code)

    st.query_params.clear()

    if "error" in result:

        st.session_state.auth_error = (
            f"Google sign-in failed: {result['error']}"
        )

    else:

        st.session_state.access_token = result.get(
            "access_token"
        )

        st.session_state.refresh_token = result.get(
            "refresh_token"
        )

        st.session_state.user_id = result.get(
            "user_id"
        )

        st.session_state.user_email = result.get(
            "email"
        )

        st.rerun()

# ---------------------------------------------------------
# LOAD CSS
# ---------------------------------------------------------

def load_css():

    css_path = (
        Path(__file__).resolve().parent
        / "assets"
        / "styles.css"
    )

    try:

        with open(css_path, "r", encoding="utf-8") as file:
            return file.read()

    except FileNotFoundError:

        return ""


st.markdown(
    f"<style>{load_css()}</style>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# NAVIGATION FUNCTION
# ---------------------------------------------------------

def set_view(view):

    st.session_state.current_view = view
    st.rerun()

# ---------------------------------------------------------
# SIGN OUT
# ---------------------------------------------------------

def sign_out():

    supabase_client.sign_out()

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user_id = None
    st.session_state.user_email = None

    st.session_state.auth_error = None
    st.session_state.auth_info = None

    st.session_state.current_view = "landing"

    st.rerun()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown("## Navigation")

    if st.button(
        "🏠 Home",
        use_container_width=True,
    ):

        set_view("landing")

    if st.button(
        "🎯 ATS Scorer",
        use_container_width=True,
    ):

        set_view("scorer")

    if st.button(
        "📊 History",
        use_container_width=True,
    ):

        set_view("history")

    if st.button(
        "📚 Resources",
        use_container_width=True,
    ):

        set_view("resources")

    st.markdown("---")

    st.markdown("### 👤 Account")

    # -----------------------------------------------------
    # SIGNED IN
    # -----------------------------------------------------

    if st.session_state.access_token:

        st.caption(
            f"Signed in as "
            f"**{st.session_state.user_email}**"
        )

        if st.button(
            "Sign out",
            use_container_width=True,
        ):

            sign_out()

    # -----------------------------------------------------
    # SIGNED OUT
    # -----------------------------------------------------

    else:

        if st.session_state.auth_error:

            st.error(
                st.session_state.auth_error
            )

            st.session_state.auth_error = None

        if st.session_state.auth_info:

            st.info(
                st.session_state.auth_info
            )

            st.session_state.auth_info = None

        # -------------------------------------------------
        # AUTH TABS
        # -------------------------------------------------

        tab_in, tab_up = st.tabs(
            [
                "Sign in",
                "Sign up",
            ]
        )

        # -------------------------------------------------
        # SIGN IN
        # -------------------------------------------------

        with tab_in:

            with st.form(
                "signin_form",
                clear_on_submit=False,
            ):

                email = st.text_input(
                    "Email",
                    key="signin_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="signin_password",
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True,
                )

            if submitted:

                if not email or not password:

                    st.session_state.auth_error = (
                        "Email and password are required."
                    )

                else:

                    result = (
                        supabase_client
                        .sign_in_with_password(
                            email,
                            password,
                        )
                    )

                    if "error" in result:

                        st.session_state.auth_error = (
                            result["error"]
                        )

                    else:

                        st.session_state.access_token = (
                            result.get(
                                "access_token"
                            )
                        )

                        st.session_state.refresh_token = (
                            result.get(
                                "refresh_token"
                            )
                        )

                        st.session_state.user_id = (
                            result.get(
                                "user_id"
                            )
                        )

                        st.session_state.user_email = (
                            result.get(
                                "email"
                            )
                        )

                        st.session_state.current_view = (
                            "scorer"
                        )

                st.rerun()

        # -------------------------------------------------
        # SIGN UP
        # -------------------------------------------------

        with tab_up:

            with st.form(
                "signup_form",
                clear_on_submit=False,
            ):

                signup_email = st.text_input(
                    "Email",
                    key="signup_email",
                )

                signup_password = st.text_input(
                    "Password (min 6 chars)",
                    type="password",
                    key="signup_password",
                )

                submitted_up = st.form_submit_button(
                    "Create account",
                    use_container_width=True,
                )

            if submitted_up:

                if not signup_email or not signup_password:

                    st.session_state.auth_error = (
                        "Email and password are required."
                    )

                else:

                    result = (
                        supabase_client
                        .sign_up_with_password(
                            signup_email,
                            signup_password,
                        )
                    )

                    if "error" in result:

                        st.session_state.auth_error = (
                            result["error"]
                        )

                    elif result.get(
                        "pending_confirmation"
                    ):

                        st.session_state.auth_info = (
                            "Check your inbox — "
                            f"confirmation email sent to "
                            f"{result['email']}."
                        )

                    else:

                        st.session_state.access_token = (
                            result.get(
                                "access_token"
                            )
                        )

                        st.session_state.refresh_token = (
                            result.get(
                                "refresh_token"
                            )
                        )

                        st.session_state.user_id = (
                            result.get(
                                "user_id"
                            )
                        )

                        st.session_state.user_email = (
                            result.get(
                                "email"
                            )
                        )

                        st.session_state.current_view = (
                            "scorer"
                        )

                st.rerun()

        # -------------------------------------------------
        # GOOGLE LOGIN
        # -------------------------------------------------

        st.markdown(
            """
            <div style="
                text-align:center;
                margin:8px 0;
                color:#94a3b8;
            ">
                or
            </div>
            """,
            unsafe_allow_html=True,
        )

        oauth = (
            supabase_client
            .google_oauth_url()
        )

        if "error" in oauth:

            st.caption(
                f"Google sign-in unavailable: "
                f"{oauth['error']}"
            )

        else:

            st.link_button(
                "Continue with Google",
                url=oauth["url"],
                use_container_width=True,
            )

# ---------------------------------------------------------
# MAIN VIEW
# ---------------------------------------------------------

if st.session_state.current_view == "landing":

    from frontend.views import landing

    landing.render()

elif st.session_state.current_view == "scorer":

    from frontend.views import scorer

    scorer.render()

elif st.session_state.current_view == "history":

    from frontend.views import history

    history.render()

elif st.session_state.current_view == "resources":

    from frontend.views import resources

    resources.render()

else:

    from frontend.views import landing

    landing.render()