# Backend Architecture Reconciliation Plan

## 1. Endpoints Inventory
**Legacy `backend/main.py`:**
- GET `/api/health`
- POST `/api/projects`
- POST `/api/projects/{project_id}/targets`
- POST `/api/scans`
- GET `/api/projects/{project_id}/assets`
- GET `/api/projects/{project_id}/findings`
- GET `/api/dashboard/{project_id}`
- GET `/api/projects/{project_id}/timeline`
- POST `/api/projects/{project_id}/reports`
- POST `/api/imports`
- GET `/api/imports`
- GET `/api/projects/{project_id}/risk`
- GET `/api/projects/{project_id}/risk/top-findings`
- GET `/api/findings/{finding_id}/risk`
- GET `/api/projects/{project_id}/graph`
- GET `/api/projects/{project_id}/risk-paths`
- POST `/api/projects/{project_id}/correlate`
- POST `/api/projects/{project_id}/snapshots/generate`
- GET `/api/projects/{project_id}/snapshots`
- GET `/api/projects/{project_id}/timeline-events`
- GET `/api/projects/{project_id}/alerts`
- POST `/api/projects/{project_id}/assistant/chat`
- PATCH `/api/findings/{finding_id}/remediation`
- GET `/api/projects/{project_id}/operations`
- GET `/api/projects/{project_id}/compliance`

**Modern `backend/app/routers/*`:**
- POST `/api/v1/projects/`
- GET `/api/v1/projects/`
- GET `/api/v1/projects/{project_id}`
- DELETE `/api/v1/projects/{project_id}`
- (Plus assets, scans, vulnerabilities routers)

## 2. Comparison & Missing Functionality
The legacy system contains our complete business logic (Risk, AI, Correlation, Diff/Snapshot, Operations, Importers, Remediation), whereas the modern system currently only holds basic CRUD operations for Projects, Assets, Scans, and Vulnerabilities. The modern system utilizes Async SQLAlchemy, whereas the legacy system uses Sync SQLAlchemy.

## 3. Migration Map
- **Models:** Merge `backend/models.py` into the canonical `backend/app/models/` module. Replace existing boilerplate models in the modern app with the robust feature-rich models from the legacy implementation.
- **Importers & AI:** Move `backend/importers.py`, `backend/scanner.py`, `backend/risk_engine.py` into their respective `backend/app/` domains (`backend/app/services/`).
- **Database:** Expand `backend/app/database.py` to securely handle both `postgresql+asyncpg://` for the API and `postgresql+psycopg2://` for the Celery workers.
- **Endpoints:** Map all `/api/*` endpoints from `legacy_main.py` into `/api/v1/*` inside `backend/app/routers/` using `AsyncSession` and `await db.execute(select(...))`.
- **Worker:** Consolidate `backend/worker.py` into `backend/app/workers/tasks.py`.
- **Frontend:** Update `frontend/lib/api.ts` to consume `/api/v1/` and dynamically utilize `NEXT_PUBLIC_API_URL` without swallowing errors.

## 4. Duplicate Routes to Remove
- `POST /api/projects` -> Use `POST /api/v1/projects/`
- `GET /api/projects/{id}/assets` -> Merge into `/api/v1/assets/`
- Legacy mock healthchecks.

## 5. Dead Modules
- `backend/main.py` (Deleted post-migration)
- `backend/models.py` (Deleted post-migration)
- `backend/database.py` (Deleted post-migration)
- `backend/worker.py` (Deleted post-migration)
