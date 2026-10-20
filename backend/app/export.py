from __future__ import annotations

import json
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .database import get_connection
from .export import export_project_schedule_to_excel
from .scheduler import calculate_schedule, generate_activity_code, generate_wbs_from_template
from .utils import generate_ai_wbs_suggestions

router = APIRouter(prefix="/api")


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: str
    project_type: Optional[str] = "construction"
    working_days: str = "1,2,3,4,5"
    weekends: str = "5,6"
    holidays: str = ""


class WBSCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None
    code: Optional[str] = None


class ActivityCreate(BaseModel):
    wbs_id: Optional[str] = None
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    duration_days: int = 1
    planned_start: Optional[str] = None
    planned_finish: Optional[str] = None
    actual_start: Optional[str] = None
    actual_finish: Optional[str] = None
    percent_complete: float = 0.0
    status: str = "not_started"


class DependencyCreate(BaseModel):
    predecessor_id: str
    successor_id: str
    dependency_type: str = "FS"
    lag_days: int = 0


class ProgressUpdate(BaseModel):
    activity_id: str
    percent_complete: float = 0.0
    actual_start: Optional[str] = None
    actual_finish: Optional[str] = None
    status: Optional[str] = None


@router.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/projects")
def list_projects():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects")
def create_project(payload: ProjectCreate):
    project_id = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO projects (id, name, description, start_date, project_type, working_days, weekends, holidays, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            project_id,
            payload.name,
            payload.description,
            payload.start_date,
            payload.project_type,
            payload.working_days,
            payload.weekends,
            payload.holidays,
        ),
    )
    conn.commit()
    conn.close()
    return {"id": project_id, "name": payload.name, "status": "created"}


@router.get("/projects/{project_id}")
def get_project(project_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return dict(row)


@router.post("/projects/{project_id}/wbs/generate")
def generate_wbs(project_id: str):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM wbs WHERE project_id = ?", (project_id,)).fetchone()
    if existing:
        rows = conn.execute("SELECT * FROM wbs WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
        conn.close()
        return {"items": [dict(row) for row in rows]}

    generated = generate_wbs_from_template(project_id)
    for entry in generated:
        conn.execute(
            "INSERT INTO wbs (id, project_id, parent_id, code, name, level, template_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                entry["id"],
                project_id,
                entry.get("parent_id"),
                entry["code"],
                entry["name"],
                entry["level"],
                entry.get("template_name"),
            ),
        )
    conn.commit()
    conn.close()
    return {"items": generated}


@router.post("/projects/{project_id}/wbs/ai")
def generate_ai_wbs(project_id: str, payload: Dict[str, Any]):
    scope_text = str(payload.get("scope_text", ""))
    project_name = str(payload.get("project_name", ""))
    return {"items": generate_ai_wbs_suggestions(scope_text, project_name)}


@router.get("/projects/{project_id}/wbs")
def list_wbs(project_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM wbs WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects/{project_id}/wbs")
def create_wbs(project_id: str, payload: WBSCreate):
    conn = get_connection()
    code = payload.code or f"WBS-{len(conn.execute('SELECT * FROM wbs WHERE project_id = ?', (project_id,)).fetchall()) + 1:02d}"
    item_id = str(uuid4())
    conn.execute(
        "INSERT INTO wbs (id, project_id, parent_id, code, name, level, template_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (item_id, project_id, payload.parent_id, code, payload.name, 1 if payload.parent_id is None else 2, "custom"),
    )
    conn.commit()
    conn.close()
    return {"id": item_id, "code": code, "name": payload.name}


@router.get("/projects/{project_id}/activities")
def list_activities(project_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM activities WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects/{project_id}/activities")
def create_activity(project_id: str, payload: ActivityCreate):
    activity_id = str(uuid4())
    code = payload.code or generate_activity_code(project_id)
    conn = get_connection()
    conn.execute(
        "INSERT INTO activities (id, project_id, wbs_id, code, name, description, duration_days, planned_start, planned_finish, actual_start, actual_finish, percent_complete, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            activity_id,
            project_id,
            payload.wbs_id,
            code,
            payload.name,
            payload.description,
            payload.duration_days,
            payload.planned_start,
            payload.planned_finish,
            payload.actual_start,
            payload.actual_finish,
            payload.percent_complete,
            payload.status,
        ),
    )
    conn.commit()
    conn.close()
    return {"id": activity_id, "code": code, "name": payload.name}


@router.get("/projects/{project_id}/dependencies")
def list_dependencies(project_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM dependencies WHERE project_id = ?", (project_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects/{project_id}/dependencies")
def create_dependency(project_id: str, payload: DependencyCreate):
    dep_id = str(uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO dependencies (id, project_id, predecessor_id, successor_id, dependency_type, lag_days, created_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
        (dep_id, project_id, payload.predecessor_id, payload.successor_id, payload.dependency_type, payload.lag_days),
    )
    conn.commit()
    conn.close()
    return {"id": dep_id, "status": "created"}


@router.post("/projects/{project_id}/schedule/calculate")
def calculate_project_schedule(project_id: str):
    return calculate_schedule(project_id)


@router.post("/projects/{project_id}/progress")
def update_progress(project_id: str, payload: ProgressUpdate):
    conn = get_connection()
    conn.execute(
        "UPDATE activities SET percent_complete = ?, actual_start = COALESCE(?, actual_start), actual_finish = COALESCE(?, actual_finish), status = ? WHERE project_id = ? AND id = ?",
        (
            payload.percent_complete,
            payload.actual_start,
            payload.actual_finish,
            payload.status or "in_progress",
            project_id,
            payload.activity_id,
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "updated"}


@router.post("/projects/{project_id}/baseline")
def create_baseline(project_id: str):
    conn = get_connection()
    activities = conn.execute("SELECT * FROM activities WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    baseline_id = str(uuid4())
    conn.execute(
        "INSERT INTO baselines (id, project_id, name, snapshot, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        (baseline_id, project_id, f"Baseline-{len(conn.execute('SELECT * FROM baselines WHERE project_id = ?', (project_id,)).fetchall()) + 1}", json.dumps([dict(row) for row in activities])),
    )
    conn.commit()
    conn.close()
    return {"id": baseline_id, "status": "created"}


@router.get("/projects/{project_id}/baseline")
def get_baseline(project_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM baselines WHERE project_id = ? ORDER BY created_at DESC LIMIT 1", (project_id,)).fetchone()
    conn.close()
    if row is None:
        return {"baseline": None}
    return {"baseline": dict(row)}


@router.get("/projects/{project_id}/export/excel")
def export_excel(project_id: str):
    path = export_project_schedule_to_excel(project_id)
    return {"file": path}


@router.get("/projects/{project_id}/summary")
def project_summary(project_id: str):
    return calculate_schedule(project_id)
