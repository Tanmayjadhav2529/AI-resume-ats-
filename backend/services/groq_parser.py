"""Compatibility wrapper for the Groq parser module.

The application historically used the typoed filename `groq_prasing.py`, but
other code imports `backend.services.groq_parser`. Keep the existing module as
canonical and expose the same API through this shim.
"""

from backend.services.groq_prasing import *  # noqa: F401,F403
