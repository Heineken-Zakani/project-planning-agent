from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


DEFAULT_TEMPLATE = [
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
    for index, name in enumerate(DEFAULT_TEMPLATE, start=1):
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
    cleaned = scope_text.strip()
    if not cleaned:
        cleaned = project_name
    tokens = [token.strip() for token in cleaned.replace("/", " ").replace("-", " ").split() if token.strip()]
    if not tokens:
        return []

    suggestions: List[Dict[str, Any]] = []
    for idx, token in enumerate(tokens[:8], start=1):
        suggestions.append(
            {
                "code": f"AI-{idx:02d}",
                "name": token.title(),
                "level": 1,
                "confidence": round(0.65 + (idx * 0.04), 2),
            }
        )
    return suggestions


def working_days_between(start_date: date, end_date: date, weekends: List[int], holidays: List[date]) -> int:
    total = 0
    current = start_date
    while current <= end_date:
        if current.weekday() in weekends:
            current += timedelta(days=1)
            continue
        if current in holidays:
            current += timedelta(days=1)
            continue
        total += 1
        current += timedelta(days=1)
    return total


def add_working_days(start_date: date, days: int, weekends: List[int], holidays: List[date]) -> date:
    if days <= 0:
        return start_date
    current = start_date
    day_count = 0
    while day_count < days:
        current += timedelta(days=1)
        if current.weekday() in weekends:
            continue
        if current in holidays:
            continue
        day_count += 1
    return current


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
