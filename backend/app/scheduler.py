from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from .database import get_connection
from .utils import (
    add_working_days,
    format_date,
    generate_wbs_template,
    parse_date,
    subtract_working_days,
)


def generate_activity_code(project_id: str) -> str:
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM activities WHERE project_id = ?",
        (project_id,),
    ).fetchone()[0]
    conn.close()
    return f"ACT-{count + 1:03d}"


def generate_wbs_from_template(project_id: str) -> List[Dict[str, Any]]:
    items = []
    for index, item in enumerate(generate_wbs_template(project_id), start=1):
        item["id"] = f"wbs-{project_id}-{index:02d}"
        items.append(item)
    return items


def calculate_schedule(project_id: str) -> Dict[str, Any]:
    conn = get_connection()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if project is None:
        conn.close()
        raise ValueError("Project not found")

    activities = conn.execute(
        "SELECT * FROM activities WHERE project_id = ? ORDER BY code",
        (project_id,),
    ).fetchall()
    dependencies = conn.execute(
        "SELECT * FROM dependencies WHERE project_id = ?",
        (project_id,),
    ).fetchall()
    conn.close()

    if not activities:
        return {
            "project_id": project_id,
            "project_start": project["start_date"],
            "project_end": project["start_date"],
            "activities": [],
            "critical_path": [],
            "summary": {"activity_count": 0, "critical_count": 0},
        }

    project_start = parse_date(project["start_date"])
    if project_start is None:
        raise ValueError("Project start date is required")

    weekend_days = [int(value) for value in str(project["weekends"]).split(",") if value.strip()]
    holiday_values = []
    for value in str(project["holidays"]).split(","):
        parsed = parse_date(value.strip())
        if parsed is not None:
            holiday_values.append(parsed)

    activity_map = {row["id"]: dict(row) for row in activities}
    predecessors = {row["id"]: [] for row in activities}
    successors = {row["id"]: [] for row in activities}

    for dep in dependencies:
        predecessors[dep["successor_id"]].append(dep["predecessor_id"])
        successors[dep["predecessor_id"]].append(dep["successor_id"])

    topo_order: List[str] = []
    visited: set[str] = set()

    def visit(activity_id: str):
        if activity_id in visited:
            return
        visited.add(activity_id)
        for next_id in successors.get(activity_id, []):
            visit(next_id)
        topo_order.append(activity_id)

    for activity in activities:
        visit(activity["id"])

    early_start: Dict[str, date] = {}
    early_finish: Dict[str, date] = {}
    for activity_id in topo_order:
        activity = activity_map[activity_id]
        if not predecessors[activity_id]:
            early_start[activity_id] = project_start
        else:
            early_start[activity_id] = max(early_finish[p] for p in predecessors[activity_id])
        duration = int(activity.get("duration_days", 1))
        early_finish[activity_id] = add_working_days(
            early_start[activity_id],
            duration,
            weekend_days,
            holiday_values,
        )

    project_end = max(early_finish.values())

    late_start: Dict[str, date] = {}
    late_finish: Dict[str, date] = {}
    for activity_id in reversed(topo_order):
        successors_for_activity = successors.get(activity_id, [])
        if not successors_for_activity:
            late_finish[activity_id] = project_end
        else:
            late_finish[activity_id] = min(late_start[s] for s in successors_for_activity)
        duration = int(activity_map[activity_id].get("duration_days", 1))
        late_start[activity_id] = subtract_working_days(
            late_finish[activity_id],
            duration,
            weekend_days,
            holiday_values,
        )

    results = []
    critical_path = []
    for activity in activities:
        activity_id = activity["id"]
        total_float = (late_start[activity_id] - early_start[activity_id]).days
        free_float = 0
        for succ in successors.get(activity_id, []):
            free_float = max(free_float, (early_start[succ] - early_finish[activity_id]).days)
        is_critical = total_float == 0

        item = {
            **dict(activity),
            "early_start": format_date(early_start[activity_id]),
            "early_finish": format_date(early_finish[activity_id]),
            "late_start": format_date(late_start[activity_id]),
            "late_finish": format_date(late_finish[activity_id]),
            "total_float": total_float,
            "free_float": free_float,
            "critical": is_critical,
        }
        results.append(item)
        if is_critical:
            critical_path.append(item)

    return {
        "project_id": project_id,
        "project_start": format_date(project_start),
        "project_end": format_date(project_end),
        "activities": results,
        "critical_path": critical_path,
        "summary": {
            "activity_count": len(results),
            "critical_count": len(critical_path),
            "project_end": format_date(project_end),
        },
    }
