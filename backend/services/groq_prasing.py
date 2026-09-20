"""Compatibility shim for the historically typoed module name `groq_prasing.py`.

All canonical Groq LLM parsing logic resides in `backend.services.groq_parser`.
"""

from backend.services.groq_parser import *  # noqa: F401,F403