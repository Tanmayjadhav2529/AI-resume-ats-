import os
from typing import Any, Dict, Optional

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _auth_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def health_check() -> Dict[str, Any]:
    response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_resume(file_obj, job_description: str = "", access_token: Optional[str] = None) -> Dict[str, Any]:
    files = {"resume": (file_obj.name, file_obj.getvalue(), file_obj.type or "application/octet-stream")}
    data = {"job_description": job_description}
    headers = _auth_headers(access_token)

    response = requests.post(
        f"{API_BASE_URL}/api/v1/analyze-resume",
        files=files,
        data=data,
        headers=headers,
        timeout=120,
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(f"Backend API error: {detail}")

    return response.json()


def generate_pdf_report(result_data: Dict[str, Any], access_token: Optional[str] = None) -> bytes:
    response = requests.post(
        f"{API_BASE_URL}/api/v1/generate-pdf",
        json=result_data,
        headers=_auth_headers(access_token),
        timeout=120,
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(f"PDF generation failed: {detail}")
    return response.content


def get_history(access_token: str) -> list:
    response = requests.get(
        f"{API_BASE_URL}/api/v1/history",
        headers=_auth_headers(access_token),
        timeout=120,
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(f"History fetch failed: {detail}")
    return response.json()


def delete_history_entry(analysis_id: str, access_token: str) -> Dict[str, Any]:
    response = requests.delete(
        f"{API_BASE_URL}/api/v1/history/{analysis_id}",
        headers=_auth_headers(access_token),
        timeout=120,
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(f"History delete failed: {detail}")
    return response.json()
