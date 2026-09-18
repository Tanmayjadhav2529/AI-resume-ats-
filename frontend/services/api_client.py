import os
from typing import Any, Dict, Optional

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def health_check() -> Dict[str, Any]:
    response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_resume(file_obj, job_description: str = "", user_id: Optional[str] = None) -> Dict[str, Any]:
    files = {"resume": (file_obj.name, file_obj.getvalue(), file_obj.type or "application/octet-stream")}
    data = {"job_description": job_description}
    if user_id:
        data["user_id"] = user_id

    response = requests.post(
        f"{API_BASE_URL}/api/v1/analyze-resume",
        files=files,
        data=data,
        timeout=120,
    )
    if response.status_code != 200:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(f"Backend API error: {detail}")

    return response.json()
