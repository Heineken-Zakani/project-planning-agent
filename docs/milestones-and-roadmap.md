# Milestones and Roadmap

## Milestone 1: Foundation and requirement alignment
Goal: set up the project structure, establish the repository standards, and lock the MVP requirements.

Planned outputs:
- updated README
- technical architecture recommendation
- MVP requirement doc
- assumptions and decisions log
- milestone tracker

Acceptance:
- repo structure is clear and maintainable
- MVP scope is documented and bounded
- assumptions are recorded

## Milestone 2: Data models and project setup
Goal: create the schema and backend foundation for projects, WBS, and activities.

Planned outputs:
- project data model
- WBS model
- activity model
- database schema
- basic API layer skeleton

Acceptance:
- a project can be created through backend services
- WBS entities can be stored and retrieved
- activity records are persisted

## Milestone 3: WBS generation and activity management
Goal: implement template-driven WBS generation and manual review/editing flow.

Planned outputs:
- WBS templates
- custom WBS creation
- AI suggestion service interface
- activity generation from WBS

Acceptance:
- user can create a WBS from template or custom structure
- generated items remain editable
- tasks can be grouped properly by project area/discipline

## Milestone 4: Dependency logic and critical path
Goal: calculate schedule dates, dependencies, and critical path.

Planned outputs:
- dependency model and API
- forward and backward pass calculations
- critical path detection
- float calculations

Acceptance:
- network calculations are deterministic and testable
- critical path and limited-float tasks are clearly identified

## Milestone 5: Progress tracking and baseline management
Goal: compare planned vs actual progress and record the schedule baseline.

Planned outputs:
- baseline creation
- progress updates
- percent complete tracking
- delay and variance detection

Acceptance:
- the system can compare planned vs actual progress
- a baseline can be saved and compared later

## Milestone 6: Gantt view and Excel export
Goal: deliver the main user-facing schedule workflow.

Planned outputs:
- Gantt visualization
- filtering and summary views
- Excel export

Acceptance:
- users can inspect the schedule visually
- schedule data can be exported to Excel for downstream use

## Milestone 7: QA and pilot readiness
Goal: harden the MVP and prepare for a controlled pilot.

Planned outputs:
- test coverage for core user workflows
- developer documentation
- release checklist
- deployment readiness notes

Acceptance:
- the core workflows pass tests
- the MVP is stable enough for pilot review
