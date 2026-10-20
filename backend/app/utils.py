from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

DEFAULT_WBS_TEMPLATE = [
    "Project Management",
    "Site Preparation",
    "Earthworks",
    "Substructure",
    "Concrete Works",
    "Mechanical Works",
    "Electrical Works",
    "Finishes",
    "Testing & Commissioning",
    "Handover",
]


def generate_wbs_template(project_id: str, template_name: str = "construction") -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for index, name in enumerate(DEFAULT_WBS_TEMPLATE, start=1):
        items.append(
            {
                "id": f"wbs-{project_id}-{index:02d}",
                "project_id": project_id,
                "parent_id": None,
                "code": f"WBS-{index:02d}",
                "name": name,
                "level": 1,
                "template_name": template_name,
            }
        )
    return items


def generate_ai_wbs_suggestions(scope_text: str, project_name: str) -> List[Dict[str, Any]]:
    cleaned = (scope_text or project_name or "").strip()
    if not cleaned:
        return []

    tokens = []
    for token in cleaned.replace("/", " ").replace("-", " ").split():
        token = token.strip()
        if token:
            tokens.append(token)

    suggestions: List[Dict[str, Any]] = []
    for index, token in enumerate(tokens[:8], start=1):
        suggestions.append(
            {
                "code": f"AI-{index:02d}",
                "name": token.title(),
                "level": 1,
                "confidence": round(0.70 + index * 0.03, 2),
            }
        )
    return suggestions


def parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def format_date(value: Optional[date]) -> Optional[str]:
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")


def add_working_days(start_date: date, days: int, weekend_days: List[int], holidays: List[date]) -> date:
    if days <= 0:
        return start_date

    current = start_date
    worked = 0
    while worked < days:
        current += timedelta(days=1)
        if current.weekday() in weekend_days:
            continue
        if current in holidays:
            continue
        worked += 1
    return current


def subtract_working_days(end_date: date, days: int, weekend_days: List[int], holidays: List[date]) -> date:
    if days <= 0:
        return end_date

    current = end_date
    worked = 0
    while worked < days:
        current -= timedelta(days=1)
        if current.weekday() in weekend_days:
            continue
        if current in holidays:
            continue
        worked += 1
    return current
