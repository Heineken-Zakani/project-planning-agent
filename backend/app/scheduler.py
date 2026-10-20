from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database import get_connection
from app.scheduler import (
    calculate_schedule,
    generate_activity_code,
    generate_wbs_from_template,
    generate_ai_wbs_suggestions,
)

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
    percent_complete: float = 0.0
    actual_start: Optional[str] = None
    actual_finish: Optional[str] = None
    status: Optional[str] = None


@router.get("/health")
def healthcheck():
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
    return {"id": project_id, "status": "created"}


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
    existing = conn.execute("SELECT id FROM wbs WHERE project_id = ?", (project_id,)).fetchall()
    if existing:
        conn.close()
        return {"items": [dict(r) for r in conn.execute("SELECT * FROM wbs WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()]}

    generated = generate_wbs_from_template(project_id)
    for item in generated:
        conn.execute(
            "INSERT INTO wbs (id, project_id, parent_id, code, name, level, template_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                item["id"],
                project_id,
                item.get("parent_id"),
                item["code"],
                item["name"],
                item["level"],
                item.get("template_name"),
            ),
        )
    conn.commit()
    conn.close()
    return {"items": generated}


@router.post("/projects/{project_id}/wbs/ai")
def generate_ai_wbs(project_id: str, payload: Dict[str, Any]):
    scope_text = str(payload.get("scope_text", ""))
    project_name = str(payload.get("project_name", ""))
    rows = generate_ai_wbs_suggestions(scope_text, project_name)
    return {"items": rows}


@router.get("/projects/{project_id}/wbs")
def list_wbs(project_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM wbs WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects/{project_id}/wbs")
def create_wbs(project_id: str, payload: WBSCreate):
    conn = get_connection()
    code = payload.code or f"WBS-{conn.execute('SELECT COUNT(*) FROM wbs WHERE project_id = ?', (project_id,)).fetchone()[0] + 1:02d}"
    wbs_id = str(uuid4())
    conn.execute(
        "INSERT INTO wbs (id, project_id, parent_id, code, name, level, template_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (wbs_id, project_id, payload.parent_id, code, payload.name, 1 if payload.parent_id is None else 2, "custom",),
    )
    conn.commit()
    conn.close()
    return {"id": wbs_id, "code": code, "name": payload.name}


@router.get("/projects/{project_id}/activities")
def list_activities(project_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM activities WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects/{project_id}/activities")
def create_activity(project_id: str, payload: ActivityCreate):
    code = payload.code or generate_activity_code(project_id)
    activity_id = str(uuid4())
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


@router.get("/projects/{project_id}/dependencies")
def list_dependencies(project_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM dependencies WHERE project_id = ?", (project_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/projects/{project_id}/schedule/calculate")
def calculate_project_schedule(project_id: str):
    result = calculate_schedule(project_id)
    return result


@router.get("/projects/{project_id}/schedule")
def get_project_schedule(project_id: str):
    conn = get_connection()
    project = dict(conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())
    activity_rows = conn.execute("SELECT * FROM activities WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    dependencies = conn.execute("SELECT * FROM dependencies WHERE project_id = ?", (project_id,)).fetchall()
    conn.close()
    return {
        "project": project,
        "activities": [dict(row) for row in activity_rows],
        "dependencies": [dict(row) for row in dependencies],
    }


@router.post("/projects/{project_id}/progress")
def update_progress(project_id: str, payload: ProgressUpdate):
    activity_id = payload.__dict__.get("activity_id")
    if not activity_id:
        raise HTTPException(status_code=400, detail="activity_id required")
    conn = get_connection()
    conn.execute(
        "UPDATE activities SET percent_complete = ?, actual_start = COALESCE(?, actual_start), actual_finish = COALESCE(?, actual_finish), status = ? WHERE project_id = ? AND id = ?",
        (
            payload.percent_complete,
            payload.actual_start,
            payload.actual_finish,
            payload.status or "in_progress",
            project_id,
            activity_id,
        ),
    )
    conn.commit()
    conn.close()
    return {"status": "updated"}


@router.post("/projects/{project_id}/baseline")
def create_baseline(project_id: str):
    conn = get_connection()
    activities = conn.execute("SELECT * FROM activities WHERE project_id = ? ORDER BY code", (project_id,)).fetchall()
    snapshot = json.dumps([dict(row) for row in activities])
    baseline_id = str(uuid4())
    conn.execute(
        "INSERT INTO baselines (id, project_id, name, snapshot, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        (baseline_id, project_id, f"Baseline-{len(conn.execute('SELECT * FROM baselines WHERE project_id = ?', (project_id,)).fetchall()) + 1}", snapshot),
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
    from app.export import export_project_schedule_to_excel

    file_name = export_project_schedule_to_excel(project_id)
    return {"file": file_name}


@router.get("/projects/{project_id}/summary")
def project_summary(project_id: str):
    schedule = calculate_schedule(project_id)
    return schedule
