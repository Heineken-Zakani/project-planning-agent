# Project Planning & Scheduling Agent

A small, reviewable MVP for construction and engineering project scheduling.

## What is implemented
- Python backend API with FastAPI
- SQLite-backed project storage
- project creation
- WBS generation from templates
- AI-assisted WBS suggestion endpoint
- activity creation
- dependency creation
- basic schedule calculation and critical-path preview
- baseline creation
- progress updates
- Excel export for schedule data

## How to run

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API checks
```bash
curl http://127.0.0.1:8000/api/health
```

## Main endpoints
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects/{project_id}/wbs/generate`
- `POST /api/projects/{project_id}/wbs/ai`
- `GET /api/projects/{project_id}/wbs`
- `POST /api/projects/{project_id}/activities`
- `GET /api/projects/{project_id}/activities`
- `POST /api/projects/{project_id}/dependencies`
- `GET /api/projects/{project_id}/dependencies`
- `POST /api/projects/{project_id}/schedule/calculate`
- `POST /api/projects/{project_id}/progress`
- `POST /api/projects/{project_id}/baseline`
- `GET /api/projects/{project_id}/export/excel`

## MVP scope
This repo intentionally covers a narrow MVP:
- project creation
- WBS generation
- activity and dependency scheduling
- critical path calculation
- baseline and progress tracking
- Excel export

Features intentionally left for future work:
- Primavera P6 compatibility
- advanced resource optimization
- S-curve reporting
- full enterprise multi-project portfolio features

## Known issues / limitations
- scheduling logic is intentionally simple and deterministic for the MVP
- dependencies and timelines should be reviewed manually
- AI suggestions are heuristics and require user validation
- authentication and roles are not yet implemented
