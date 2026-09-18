from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "template"


def _build_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml"), default_for_string=False),
    )
    env.filters["format_date"] = lambda value: value if value else "—"
    return env


def generate_html_reports(data: Dict[str, Any]) -> Dict[str, str]:
    """Render the ATS report templates and return them by name."""
    env = _build_env()
    templates = {
        "summary": env.get_template("summary.html"),
        "action_items": env.get_template("action_items.html"),
        "jd_comparison": env.get_template("jd_comparison.html"),
        "quick_actions": env.get_template("quick_actions.html"),
    }

    rendered: Dict[str, str] = {}
    for name, template in templates.items():
        rendered[name] = template.render(**data)

    return rendered
