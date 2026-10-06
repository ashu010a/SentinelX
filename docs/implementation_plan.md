# SentinelX Implementation Plan

## Phase 1: Infrastructure & Foundation (Week 1)
- **Goal:** Establish the production-ready infrastructure.
- **Tasks:**
  - Create `docker-compose.yml` for PostgreSQL, Redis, Celery Worker, FastAPI, and Next.js.
  - Initialize Alembic for database migrations.
  - Implement base SQLAlchemy models and Pydantic schemas.

## Phase 2: Core API & Auth (Week 2)
- **Goal:** Secure boundaries and basic CRUD.
- **Tasks:**
  - Implement JWT authentication and RBAC.
  - Build endpoints for Projects, Targets, and Assets.
  - Configure structured logging and error handling.

## Phase 3: Worker Architecture & Adapters (Week 3)
- **Goal:** Asynchronous job execution and normalized parsing.
- **Tasks:**
  - Setup Celery and Redis broker.
  - Define `BaseScannerAdapter` interface.
  - Implement initial adapters: `SubfinderAdapter`, `NmapAdapter`, `HttpxAdapter`.

## Phase 4: Finding Normalization & Correlation (Week 4)
- **Goal:** Store actionable intel.
- **Tasks:**
  - Implement normalization pipeline to parse raw adapter output into Postgres `Findings` and `Evidence`.
  - Build correlation logic to group findings by root cause.

## Phase 5: Frontend Overhaul (Week 5)
- **Goal:** Professional UI.
- **Tasks:**
  - Migrate current React components to `shadcn/ui`.
  - Implement Recharts for the Dashboard (Risk Scoring, Trends).
  - Build real-time scan job status polling.
