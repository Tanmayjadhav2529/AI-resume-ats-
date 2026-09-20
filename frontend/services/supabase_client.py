import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from supabase import create_client, Client


# Load variables from .env
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
AUTH_REDIRECT_URL = os.getenv(
    "AUTH_REDIRECT_URL",
    "http://localhost:8501"
)


_supabase_client: Optional[Client] = None


def _get_client() -> Optional[Client]:
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None

    _supabase_client = create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY
    )

    return _supabase_client


def sign_in_with_password(
    email: str,
    password: str
) -> Dict[str, Any]:

    client = _get_client()

    if client is None:
        return {
            "error": (
                "Supabase client is not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY."
            )
        }

    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        session = getattr(response, "session", None)
        user = getattr(response, "user", None)

        if not session or not user:
            return {
                "error": "Sign-in failed. Please check your credentials."
            }

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user_id": user.id,
            "email": user.email,
        }

    except Exception as exc:
        return {"error": str(exc)}


def sign_up_with_password(
    email: str,
    password: str
) -> Dict[str, Any]:

    client = _get_client()

    if client is None:
        return {
            "error": (
                "Supabase client is not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY."
            )
        }

    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })

        user = getattr(response, "user", None)
        session = getattr(response, "session", None)

        if not user:
            return {"error": "Sign-up failed."}

        # Email confirmation required
        if session is None:
            return {
                "pending_confirmation": True,
                "email": user.email,
                "user_id": user.id,
                "message": (
                    "Please check your email to confirm your account."
                ),
            }

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user_id": user.id,
            "email": user.email,
            "pending_confirmation": False,
        }

    except Exception as exc:
        return {"error": str(exc)}


def sign_out() -> Dict[str, Any]:

    client = _get_client()

    if client is None:
        return {
            "error": "Supabase client is not configured."
        }

    try:
        client.auth.sign_out()

        return {"success": True}

    except Exception as exc:
        return {"error": str(exc)}


def google_oauth_url() -> Dict[str, Any]:

    client = _get_client()

    if client is None:
        return {
            "error": (
                "Supabase client is not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY."
            )
        }

    try:
        response = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": AUTH_REDIRECT_URL
            }
        })

        # supabase-py normally returns an object containing the URL
        url = getattr(response, "url", None)

        if url:
            return {"url": url}

        if isinstance(response, dict):
            return {"url": response.get("url", "")}

        return {"url": str(response)}

    except Exception as exc:
        return {"error": str(exc)}


def exchange_code_for_session(
    code: str
) -> Dict[str, Any]:

    client = _get_client()

    if client is None:
        return {
            "error": (
                "Supabase client is not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY."
            )
        }

    try:
        response = client.auth.exchange_code_for_session({
            "auth_code": code
        })

        session = getattr(response, "session", None)
        user = getattr(response, "user", None)

        if not session or not user:
            return {
                "error": (
                    "Google sign-in did not return "
                    "a valid session."
                )
            }

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user_id": user.id,
            "email": user.email,
        }

    except Exception as exc:
        return {"error": str(exc)}