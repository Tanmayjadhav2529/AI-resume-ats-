from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "template"


def _build_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml"), default_for_string=False),
    )
    env.filters["format_date"] = lambda value: str(value) if value else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return env


def generate_html_reports(data: Dict[str, Any]) -> Dict[str, str]:
    """Render the ATS report templates and return them by name."""
    env = _build_env()

    context = dict(data)

    # 1. Overall Score & Score Color
    score = float(context.get("ATS_score") or context.get("ats_score") or 0.0)
    context["overall_score"] = score
    if score >= 80:
        context["score_color"] = "#16a34a"  # Green
    elif score >= 60:
        context["score_color"] = "#d97706"  # Amber
    else:
        context["score_color"] = "#dc2626"  # Red

    # 2. Timestamp
    if not context.get("timestamp"):
        context["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 3. Component Scores & Component Percentages
    comp_scores = context.get("component_scores") or {}
    if hasattr(comp_scores, "model_dump"):
        comp_scores = comp_scores.model_dump()
    context["component_scores"] = comp_scores

    component_max = {
        "formatting": 20.0,
        "keywords": 25.0,
        "content": 25.0,
        "skill_validation": 15.0,
        "ats_compatibility": 15.0,
    }
    comp_pct = {}
    for key, max_val in component_max.items():
        val = float(comp_scores.get(key, 0.0))
        comp_pct[key] = min(100.0, max(0.0, (val / max_val) * 100.0))
    context["component_pct"] = comp_pct

    # 4. Skill Validation details
    svd = context.get("skill_validation_details") or {}
    if hasattr(svd, "model_dump"):
        svd = svd.model_dump()
    context["total_skills"] = svd.get("total", len(context.get("skills", [])))
    context["validated_count"] = svd.get("validated_count", len(svd.get("validated", [])))
    context["validation_pct"] = svd.get("validation_pct", 0.0)
    context["validated_skills"] = svd.get("validated", [])
    context["unvalidated_skills"] = svd.get("unvalidated", [])

    # 5. Feedback Issue Lists by Priority
    raw_feedback = context.get("detailed_feedback") or []
    feedback_list = []
    for item in raw_feedback:
        if hasattr(item, "model_dump"):
            feedback_list.append(item.model_dump())
        elif isinstance(item, dict):
            feedback_list.append(item)

    high_prio = []
    med_prio = []
    low_prio = []
    for item in feedback_list:
        sev = (item.get("severity_level") or item.get("severity") or "low").lower()
        if sev in ("high", "critical"):
            high_prio.append(item)
        elif sev in ("medium", "moderate"):
            med_prio.append(item)
        else:
            low_prio.append(item)

    context["all_feedback"] = feedback_list
    context["high_priority"] = high_prio
    context["medium_priority"] = med_prio
    context["low_priority"] = low_prio

    # 6. JD Analysis
    jd_analysis = context.get("jd_comparison") or context.get("jd_match_analysis")
    if hasattr(jd_analysis, "model_dump"):
        jd_analysis = jd_analysis.model_dump()
    context["jd_analysis"] = jd_analysis

    templates = {
        "summary": env.get_template("summary.html"),
        "action_items": env.get_template("action_items.html"),
        "jd_comparison": env.get_template("jd_comparison.html"),
        "quick_actions": env.get_template("quick_actions.html"),
    }

    rendered: Dict[str, str] = {}
    for name, template in templates.items():
        rendered[name] = template.render(**context)

    return rendered
