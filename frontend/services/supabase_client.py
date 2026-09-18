import os
from typing import Any, Dict, Optional

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

_supabase_client: Optional[Client] = None


def _get_client() -> Optional[Client]:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    _supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase_client


def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"error": "Supabase client is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."}
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        session = getattr(response, "session", None)
        user = getattr(response, "user", None)
        if not session or not user:
            return {"error": "Sign-in failed. Please check your credentials."}
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user_id": user.id,
            "email": user.email,
        }
    except Exception as exc:  # pragma: no cover - wrapped for UI
        return {"error": str(exc)}


def sign_up_with_password(email: str, password: str) -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"error": "Supabase client is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."}
    try:
        response = client.auth.sign_up({"email": email, "password": password})
        user = getattr(response, "user", None)
        if getattr(response, "email_confirmed_at", None) is None and user is not None:
            return {
                "pending_confirmation": True,
                "email": user.email,
                "user_id": user.id,
                "message": "Please check your email to confirm your account.",
            }
        if not user:
            return {"error": "Sign-up failed."}
        return {
            "access_token": getattr(getattr(response, "session", None), "access_token", None),
            "refresh_token": getattr(getattr(response, "session", None), "refresh_token", None),
            "user_id": user.id,
            "email": user.email,
            "pending_confirmation": False,
        }
    except Exception as exc:  # pragma: no cover - wrapped for UI
        return {"error": str(exc)}


def sign_out() -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"error": "Supabase client is not configured."}
    try:
        client.auth.sign_out()
        return {"success": True}
    except Exception as exc:  # pragma: no cover - wrapped for UI
        return {"error": str(exc)}


def google_oauth_url() -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"error": "Supabase client is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."}
    try:
        url = client.auth.sign_in_with_oauth({"provider": "google", "redirect_to": "http://localhost:8501"})
        if isinstance(url, dict):
            return {"url": url.get("url", "")}
        return {"url": str(url)}
    except Exception as exc:  # pragma: no cover - wrapped for UI
        return {"error": str(exc)}


def exchange_code_for_session(code: str) -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {"error": "Supabase client is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."}
    try:
        response = client.auth.exchange_code_for_session({"auth_code": code})
        session = getattr(response, "session", None)
        user = getattr(response, "user", None)
        if not session or not user:
            return {"error": "Google sign-in did not return a valid session."}
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user_id": user.id,
            "email": user.email,
        }
    except Exception as exc:  # pragma: no cover - wrapped for UI
        return {"error": str(exc)}
