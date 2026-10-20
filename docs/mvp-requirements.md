# MVP Requirements and Scope

## 1. Repository state
The repository was newly initialized and contains only the default GitHub bootstrap files: `.gitignore`, `LICENSE`, and a placeholder `README.md`.

There is no functional application code, no PRD document, and no project implementation yet.

## 2. Source of truth
The available source of truth for this project is the user-provided product brief and the explicit MVP direction:
- project planning and scheduling agent for construction, civil engineering, and oil & gas projects
- WBS generation should support both template-based and AI-assisted workflows
- focus on the MVP core features only
- keep Primavera P6, S-curves, resource optimization, and advanced AI analysis out of the MVP unless later requirements say otherwise

## 3. Confirmed MVP requirements
The user explicitly requested the following MVP scope:
- project creation
- WBS generation
- activity scheduling
- dependency management
- critical-path analysis
- Gantt chart visualization
- progress tracking
- Excel export
- calendar configuration for working days, weekends, and public holidays

Additional requirements from the product brief that remain in scope for MVP:
- users must be able to create and edit a WBS hierarchy
- users must be able to generate activity IDs and review them
- users must be able to define dependencies and logical relationships
- users must be able to calculate float and identify limited-float activities
- users must be able to save a baseline schedule and compare actual vs planned progress
- the application should present a professional web UI

## 4. Requirements that are not in the MVP
The following are explicitly treated as future work and excluded from MVP unless product direction changes:
- Primavera P6 compatibility
- resource optimization and leveling
- S-curve generation
- advanced AI schedule analytics
- earned value management
- multi-project portfolio planning
- large-scale external integrations

## 5. WBS generation decision
Confirmed direction from the user:
- template-based WBS generation is required for reliability
- AI-assisted WBS generation is project direction for MVP
- both must be supported in the design
- generated WBS items must remain editable, reviewable, and reorganizable before finalization

This means the MVP default should be:
- use a built-in template-driven WBS generator as the baseline path
- allow AI-assisted generation as an optional assistive path that can propose structure, tasks, and grouping
- keep the final WBS editable and not automatically finalised without user validation

## 6. Assumptions and reversible defaults
The following assumptions are used to keep implementation moving without blocking the MVP:
- single-project scheduling is the initial scope; multi-project portfolio features are deferred
- project planning will be browser-based, not mobile-first
- user authentication is needed for protection but is not treated as a blocking differentiator for the MVP design
- AI provider choice will be abstracted behind a service interface so the final provider can be swapped later
- generated schedules will use a simple, explainable calculation engine rather than a heavy optimization solver in the MVP

## 7. Decisions that would materially change the product
The following product choices would materially alter scope or architecture and should be treated as open questions until confirmed:
- whether authentication and roles are required for MVP or can be deferred
- whether project data is single-tenant or multi-tenant
- whether Excel export is limited to project schedule tables or should also include reports and summary sheets
- whether AI assistance is optional or required for WBS generation in the initial release
- whether a first-party scheduling engine is required or whether a thin wrapper around external scheduling logic is acceptable

## 8. MVP acceptance focus
The implementation should deliver a working, reviewable core schedule workflow with:
1. project creation
2. WBS authoring
3. activity creation and editing
4. dependency logic
5. critical path calculation
6. baseline and progress updates
7. Gantt chart
8. Excel export

This should be sufficient for a pilot project and for validating real-world planning workflows.
