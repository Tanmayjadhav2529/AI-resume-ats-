import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger('ats_resume_scorer')

COMMON_TYPOS = {
    'teh': 'the',
    'recieve': 'receive',
    'seperate': 'separate',
    'experiance': 'experience',
    'responsibile': 'responsible',
    'managment': 'management',
    'devoloper': 'developer',
    'enginner': 'engineer',
    'acheived': 'achieved',
    'sucessful': 'successful',
    'maintainance': 'maintenance',
    'implimented': 'implemented',
    'definately': 'definitely',
    'referance': 'reference',
}

PASSIVE_VOICE_PATTERNS = [
    r'\bwas\s+\w+ed\s+by\b',
    r'\bwere\s+\w+ed\s+by\b',
    r'\bwas\s+responsible\s+for\b',
    r'\bwere\s+assigned\s+to\b',
]


def analyze_grammar(text: str) -> Dict[str, Any]:
    """
    Lightweight, deterministic grammar and stylistic quality analyzer for resumes.
    Returns structured results for scoring, feedback, and recommendations.
    """
    if not text or not text.strip():
        return {
            "total_errors": 0,
            "critical_errors": [],
            "moderate_errors": [],
            "minor_errors": [],
            "warnings": [],
            "penalty_applied": 0.0,
            "errors": [],
            "quality_score": 100.0,
        }

    try:
        critical_errors: List[Dict[str, Any]] = []
        moderate_errors: List[Dict[str, Any]] = []
        minor_errors: List[Dict[str, Any]] = []
        warnings: List[str] = []
        errors_summary: List[str] = []

        # 1. Repeated word check (e.g. "the the", "in in")
        repeated_word_matches = re.finditer(r'\b([a-zA-Z]{2,})\s+\1\b', text, re.IGNORECASE)
        seen_repeats = set()
        for match in repeated_word_matches:
            word = match.group(1).lower()
            if word not in seen_repeats and word not in {'ha', 'la'}:
                seen_repeats.add(word)
                msg = f"Repeated consecutive word: '{match.group(0)}'"
                critical_errors.append({
                    "error_text": match.group(0),
                    "suggestions": [word],
                    "message": msg,
                    "category": "duplicate_word"
                })
                errors_summary.append(msg)

        # 2. Common spelling typos in tech resumes
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        seen_typos = set()
        for w in words:
            w_lower = w.lower()
            if w_lower in COMMON_TYPOS and w_lower not in seen_typos:
                seen_typos.add(w_lower)
                correction = COMMON_TYPOS[w_lower]
                msg = f"Possible spelling error: '{w}' -> '{correction}'"
                critical_errors.append({
                    "error_text": w,
                    "suggestions": [correction],
                    "message": msg,
                    "category": "spelling"
                })
                errors_summary.append(msg)

        # 3. Passive voice overuse check
        passive_count = 0
        for pattern in PASSIVE_VOICE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            passive_count += len(matches)

        if passive_count >= 3:
            msg = f"Overuse of passive voice ({passive_count} instances detected). Use strong active verbs."
            moderate_errors.append({
                "error_text": "Passive voice overuse",
                "suggestions": ["Use active past-tense verbs (e.g., 'Developed', 'Led')"],
                "message": msg,
                "category": "style"
            })
            errors_summary.append(msg)
            warnings.append(msg)

        # 4. Excessive punctuation check (e.g. "!!" or "??")
        exclamation_matches = re.findall(r'[!?]{2,}', text)
        if exclamation_matches:
            msg = "Avoid multiple consecutive exclamation marks or question marks in professional resumes."
            minor_errors.append({
                "error_text": exclamation_matches[0],
                "suggestions": ["."],
                "message": msg,
                "category": "punctuation"
            })
            errors_summary.append(msg)

        # Calculate penalty
        total_errors = len(critical_errors) + len(moderate_errors) + len(minor_errors)
        penalty = (len(critical_errors) * 1.5) + (len(moderate_errors) * 0.8) + (len(minor_errors) * 0.3)
        penalty_applied = round(min(10.0, penalty), 1)
        quality_score = round(max(0.0, 100.0 - (penalty_applied * 5.0)), 1)

        return {
            "total_errors": total_errors,
            "critical_errors": critical_errors,
            "moderate_errors": moderate_errors,
            "minor_errors": minor_errors,
            "warnings": warnings,
            "penalty_applied": penalty_applied,
            "errors": errors_summary,
            "quality_score": quality_score,
        }

    except Exception as exc:
        logger.warning(f"Grammar analysis encountered an error: {exc}. Using clean fallback.")
        return {
            "total_errors": 0,
            "critical_errors": [],
            "moderate_errors": [],
            "minor_errors": [],
            "warnings": [],
            "penalty_applied": 0.0,
            "errors": [],
            "quality_score": 100.0,
        }
