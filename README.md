# Project Planning & Scheduling Agent

AI-powered project planning and scheduling web application for construction, civil engineering, and oil & gas projects.

## Overview
This repository is being developed as a web application that helps planners and project control engineers:
- generate schedules from BOQ, scope of work, or activity lists
- build a WBS and assign activity IDs
- create dependencies and calculate critical path
- compare actual vs planned progress
- visualize schedules in a Gantt view
- export project data to Excel

The current repository is in early bootstrap mode. It contains the initial GitHub project scaffold, but no application code yet.

## Current Repository Status
- Repository initialized successfully
- Core project files present: README, LICENSE, .gitignore
- No functional application code found yet
- No PRD was found in the repo, so product requirements are being documented in `docs/` based on the project brief and the explicit MVP direction provided

## Confirmed MVP Direction
The current project direction explicitly supports both:
- template-based WBS generation
- AI-assisted WBS generation

The MVP will focus on:
1. project creation
2. WBS generation
3. schedule logic and dependencies
4. critical path
5. progress tracking
6. Gantt chart
7. Excel export

Later enhancements remain explicitly out of scope for MVP, including:
- Primavera P6 compatibility
- resource optimization
- S-curves
- advanced AI analysis

## Recommended Architecture
The product is planned as a modular web app with:
- frontend: React + TypeScript
- backend: Python + FastAPI
- database: PostgreSQL
- scheduling logic: Python-based network analysis with optional graph utilities
- export layer: Excel generation via Python
- AI-assisted planning: OpenAI-compatible APIs with human review before applying suggestions

## Repository Structure
```text
project-planning-agent/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── assumptions-and-decisions.md
│   ├── architecture.md
│   ├── mvp-requirements.md
│   └── milestones-and-roadmap.md
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
├── database/
│   ├── schema.sql
│   └── migrations/
├── .github/
│   └── workflows/
└── tests/
```

## MVP Milestones
1. Foundation and requirements alignment
2. Data models and project setup
3. WBS generation and activity creation
4. Dependency logic and critical path
5. Progress tracking and baseline updates
6. Gantt chart and Excel export
7. QA, documentation, and pilot readiness

## Assumptions and Decisions
- Template-based WBS is a required MVP fallback for reliability
- AI-assisted WBS is allowed in MVP, but must remain reviewable and editable
- No native Primavera P6 compatibility in MVP unless a later requirement explicitly mandates it
- User roles and multi-user access are not yet a blocker to the MVP unless product scope requires them

## Development Notes
- Keep the MVP intentionally narrow and reviewable
- Prefer simple, explainable scheduling logic over premature optimization
- Avoid introducing large dependency sets before the core workflow is working
- Keep the README and issue list aligned with actual build status

## Next Steps
The next work is to finalize the product foundation, capture the requirements in docs, and begin implementing the MVP in feature order.
