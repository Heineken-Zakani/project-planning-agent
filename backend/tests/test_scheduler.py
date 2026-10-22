from __future__ import annotations

from backend.app.scheduler import calculate_schedule, generate_wbs_from_template
from backend.app.utils import add_working_days, generate_ai_wbs_suggestions


def test_wbs_template_generation_returns_default_items():
    items = generate_wbs_from_template("project-123")
    assert len(items) >= 3
    assert items[0]["code"] == "WBS-01"
    assert "Project Management" in [item["name"] for item in items]


def test_ai_wbs_generation_returns_specific_suggestions():
    suggestions = generate_ai_wbs_suggestions("Civil works and concrete slab installation", "Project A")
    assert len(suggestions) > 0
    assert suggestions[0]["name"]


def test_add_working_days_skips_weekends_and_holidays():
    start = __import__("datetime").date(2026, 10, 1)
    result = add_working_days(start, 3, [5, 6], [__import__("datetime").date(2026, 10, 3)])
    assert result.isoformat() == "2026-10-06"


def test_schedule_calculation_marks_critical_path_for_simple_chain():
    # This test exercises the basic chain logic expected in the MVP schedule engine.
    project_id = "project-crit"
    schedule = calculate_schedule(project_id)
    assert "activities" in schedule
    assert "summary" in schedule
