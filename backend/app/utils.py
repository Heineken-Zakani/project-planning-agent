from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from app.database import get_connection
from app.utils import add_working_days, format_date, generate_ai_wbs_suggestions, generate_wbs_template, parse_date, working_days_between


def generate_activity_code(project_id: str) -> str:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM activities WHERE project_id = ?", (project_id,)).fetchone()[0]
    conn.close()
    return f"ACT-{count + 1:03d}"


def generate_wbs_from_template(project_id: str) -> List[Dict[str, Any]]:
    items = generate_wbs_template(project_id)
    for item in items:
        item["id"] = str(uuid4())
    return items


def generate_ai_wbs_suggestions(scope_text: str, project_name: str) -> List[Dict[str, Any]]:
    return generate_ai_wbs_suggestions(scope_text, project_name)


def calculate_schedule(project_id: str) -> Dict[str, Any]:
    conn = get_connection()
    project = dict(conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())
    activities = [dict(row) for row in conn.execute("SELECT * FROM activities WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()]
    dependencies = [dict(row) for row in conn.execute("SELECT * FROM dependencies WHERE project_id = ?", (project_id,)).fetchall()]
    conn.close()

    if not activities:
        return {"project_id": project_id, "activities": [], "critical_path": [], "project_end": None}

    working_days = [int(item) for item in str(project.get("working_days", "1,2,3,4,5")).split(",") if item.strip()]
    weekend_days = [int(item) for item in str(project.get("weekends", "5,6")).split(",") if item.strip()]
    holiday_dates = []
    for item in str(project.get("holidays", "")).split(","):
        if not item.strip():
            continue
        parsed = parse_date(item.strip())
        if parsed is not None:
            holiday_dates.append(parsed)

    project_start = parse_date(project["start_date"])
    if project_start is None:
        raise ValueError("Project start date is required")

    activity_map = {activity["id"]: activity for activity in activities}
    successors = {activity["id"]: [] for activity in activities}
    predecessors = {activity["id"]: [] for activity in activities}

    for dep in dependencies:
        pred = dep["predecessor_id"]
        succ = dep["successor_id"]
        successors[pred].append(succ)
        predecessors[succ].append(pred)

    early_start: Dict[str, date] = {}
    early_finish: Dict[str, date] = {}
    late_start: Dict[str, date] = {}
    late_finish: Dict[str, date] = {}
    order: List[str] = []
    visited: set[str] = set()

    def topo(node_id: str):
        if node_id in visited:
            return
        visited.add(node_id)
        for succ in successors.get(node_id, []):
            topo(succ)
        order.append(node_id)

    for activity in activities:
        topo(activity["id"])

    for activity_id in order:
        activity = activity_map[activity_id]
        if not predecessors[activity_id]:
            es = project_start
        else:
            es = max(
                [early_finish[pred] for pred in predecessors[activity_id]],
                default=project_start,
            )
        duration = int(activity.get("duration_days", 1))
        ef = add_working_days(es, duration, weekend_days, holiday_dates)
        early_start[activity_id] = es
        early_finish[activity_id] = ef

    project_end = max(early_finish.values(), default=project_start)
    for activity_id in reversed(order):
        if not successors[activity_id]:
            ls = project_end
            lf = project_end
        else:
            min_lf = min([early_start[succ] for succ in successors[activity_id]])
            ls = min_lf
            lf = min_lf
        late_start[activity_id] = ls
        late_finish[activity_id] = lf

    # This assignment is deliberately simple and deterministic for MVP.
    # We compute total float as the gap between early and late schedule positions.
    results = []
    for activity in activities:
        activity_id = activity["id"]
        duration = int(activity.get("duration_days", 1))
        es = early_start[activity_id]
        ef = early_finish[activity_id]
        ls = late_start.get(activity_id, es)
        lf = late_finish.get(activity_id, ef)
        total_float = (ls - es).days
        free_float = max(0, (min([early_start[s] for s in successors.get(activity_id, [])], default=es) - ef).days)
        is_critical = total_float == 0
        activity_record = {
            **activity,
            "early_start": format_date(es),
            "early_finish": format_date(ef),
            "late_start": format_date(ls),
            "late_finish": format_date(lf),
            "total_float": total_float,
            "free_float": free_float,
            "critical": is_critical,
        }
        results.append(activity_record)

    critical_path = [a for a in results if a["critical"]]

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
