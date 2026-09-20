from typing import Any, Dict, Optional, Callable, Tuple
import logging


# =========================================================
# LOGGING
# =========================================================

logger = logging.getLogger("ats_resume_scorer")


def log_error(
    error: Exception,
    context: str = ""
) -> None:
    """Log an error with optional context."""

    if context:
        logger.error(
            f"[{context}] {error}",
            exc_info=True
        )
    else:
        logger.error(
            str(error),
            exc_info=True
        )


def log_warning(
    message: str,
    context: str = ""
) -> None:
    """Log a warning with optional context."""

    if context:
        logger.warning(
            f"[{context}] {message}"
        )
    else:
        logger.warning(message)


def log_info(
    message: str,
    context: str = ""
) -> None:
    """Log an informational message with optional context."""

    if context:
        logger.info(
            f"[{context}] {message}"
        )
    else:
        logger.info(message)


# =========================================================
# EXCEPTIONS
# =========================================================

class FileParsingError(Exception):
    """Raised when a file cannot be parsed."""
    pass


class TextExtractionError(Exception):
    """Raised when text cannot be extracted from a file."""

    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
    ):
        super().__init__(message)
        self.user_message = user_message


class FileUploadError(Exception):
    """Raised when an uploaded file cannot be processed."""
    pass


# =========================================================
# FALLBACK HELPER
# =========================================================

def with_fallback(
    primary_func: Callable,
    fallback_func: Callable,
    data: Any,
    log_fallback: bool = False,
) -> Tuple[Any, bool]:
    """
    Try the primary function first.

    If it fails, use the fallback function.

    Returns:
        (result, used_fallback)
    """

    try:

        result = primary_func(data)

        return result, False

    except Exception as primary_error:

        if log_fallback:
            log_warning(
                f"Primary extraction failed: {primary_error}. "
                "Trying fallback.",
                context="with_fallback"
            )

        try:

            result = fallback_func(data)

            return result, True

        except Exception as fallback_error:

            log_error(
                fallback_error,
                context="with_fallback"
            )

            raise fallback_error


# =========================================================
# DEFAULT ANALYSIS RESULTS
# =========================================================

def get_default_grammar_results() -> Dict[str, Any]:
    return {
        "critical_errors": [],
        "moderate_errors": [],
        "minor_errors": [],
        "total_errors": 0,
        "penalty_applied": 0.0,
        "quality_score": 100.0,
    }


def get_default_location_results() -> Dict[str, Any]:
    return {
        "location_found": False,
        "detected_locations": [],
        "privacy_risk": "none",
        "recommendations": [],
        "penalty_applied": 0.0,
    }


def get_default_skill_validation_results() -> Dict[str, Any]:
    return {
        "validated_skills": [],
        "unvalidated_skills": [],
        "validation_percentage": 0.0,
        "skill_project_mapping": {},
        "validation_score": 0.0,
        "validated": [],
        "unvalidated": [],
        "total": 0,
        "validated_count": 0,
        "validation_pct": 0.0,
    }