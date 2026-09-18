from typing import Any, Dict


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
