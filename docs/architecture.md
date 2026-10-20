# Architecture and Implementation Recommendation

## 1. Product architecture
The recommended architecture is a modular web application with clear separation between:
- frontend presentation
- backend APIs and business logic
- schedule calculation engine
- data persistence
- AI assistance
- export services

## 2. Recommended technology stack
### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS or CSS Modules
- a lightweight charting library for Gantt rendering

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

### Scheduling logic
- Python-based deterministic schedule calculations for the MVP
- optional `networkx` for dependency graph logic if useful
- keep the scheduling engine separate from the API layer for clarity and testing

### AI layer
- OpenAI-compatible API or Azure OpenAI
- a provider abstraction that allows swapping providers without changing schedule logic
- AI suggestions must be reviewable and editable before final application

### Export and data processing
- `pandas` and `openpyxl` for Excel export
- CSV/Excel import for BOQ and project data

## 3. Recommended code layout
```text
project-planning-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── config.py
│   │   └── main.py
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
├── docs/
├── tests/
└── README.md
```

## 4. Domain model recommendations
The MVP should support these core entities:
- Project
- WBS
- Activity
- Dependency
- Calendar
- Baseline
- ProgressUpdate
- BOQItem

## 5. Key architectural decisions
- Keep scheduling calculations in a dedicated service layer rather than in API handlers
- Use a relational database rather than a document store for schedule data and dependency integrity
- Keep AI operations behind a service boundary so the rest of the app can operate even when AI is unavailable
- Prefer simple, testable logic over optimization complexity in the MVP

## 6. Technical risks and mitigations
### Risk: AI is unreliable or unavailable
Mitigation: provide template-based WBS generation as the default and keep AI as assistive, not mandatory.

### Risk: schedule calculations become complex quickly
Mitigation: use a deterministic calculation engine with unit-tested logic for critical path and float.

### Risk: export and data validation become inconsistent
Mitigation: centralize export schema validation and testing.

### Risk: Architecture becomes over-engineered too early
Mitigation: start with the MVP workflow only; add more layers only when product needs demand them.
