"""Compatibility shim for typo filename `report.generator.py`.

All canonical recommendation logic resides in `backend.services.recommendation_engine`.
"""

from backend.services.recommendation_engine import *  # noqa: F401,F403
