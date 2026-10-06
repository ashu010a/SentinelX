import os

docs_dir = "docs"
os.makedirs(docs_dir, exist_ok=True)

files = {}

files["implementation_plan.md"] = """# SentinelX Implementation Plan

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
"""

files["architecture.md"] = """# System Architecture

## Overview
SentinelX follows a modular, async-driven architecture separating the API presentation layer from heavy security scanning workloads.

## Components
1. **Frontend (Next.js):** SSR/SSG capable React application using Tailwind and shadcn/ui.
2. **API Backend (FastAPI):** High-performance Python API handling routing, auth, and DB sessions.
3. **Task Queue (Celery + Redis):** Manages long-running security scans (Nmap, Nuclei) without blocking the API.
4. **Database (PostgreSQL):** Relational store for normalized findings, assets, and configurations.

## Architecture Diagram (Mermaid)
```mermaid
graph TD
    Client[Browser] -->|REST/HTTP| API[FastAPI Backend]
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Dispatch Job| Queue[(Redis)]
    Queue --> Worker[Celery Worker]
    Worker -->|Execute| Scanner[External Tool: Nmap, Nuclei, etc.]
    Scanner -->|Raw Output| Worker
    Worker -->|Normalize| DB
```

## Security Pipeline
Target -> Subfinder -> Dnsx -> Naabu/Nmap -> Httpx -> Nuclei -> Result Normalization -> DB
"""

files["database_design.md"] = """# Database Design

## Core Entities
- **User:** Authentication and authorization details.
- **Project:** Organizational container for targets and scans.
- **Target:** The root domain or IP range authorized for scanning.
- **Asset / Domain / IP:** Discovered infrastructure components.
- **Service:** Discovered open ports/protocols on IPs.
- **Endpoint:** Discovered web URLs/APIs.
- **ScanJob:** Metadata about a Celery task (status, tool, progress).
- **Finding:** A normalized security vulnerability or misconfiguration.
- **Evidence:** Raw scanner output or proof linking to a Finding.

## Relationships
- Project (1) -> (N) Target
- Target (1) -> (N) Domain
- Domain (N) -> (M) IP
- IP (1) -> (N) Service
- Asset (1) -> (N) Finding
- ScanJob (1) -> (N) Finding
"""

files["api_design.md"] = """# API Design

## Design Principles
- **RESTful:** Standard HTTP methods (GET, POST, PUT, DELETE).
- **Pagination:** Offset/Limit based pagination for all list endpoints.
- **Standardized Responses:** envelope for data, standard error schemas.

## Core Endpoints
- `POST /api/v1/auth/token` - Authenticate and get JWT.
- `GET /api/v1/projects` - List projects.
- `POST /api/v1/projects/{id}/scans` - Dispatch a new ScanJob to Celery.
- `GET /api/v1/scans/{id}` - Poll ScanJob status.
- `GET /api/v1/assets` - Filterable list of discovered assets.
- `GET /api/v1/findings` - List normalized security findings.
"""

files["scanner_adapter_design.md"] = """# Scanner Adapter Design

## Principles
1. **Decoupling:** The core backend does not know how Nuclei or Nmap works.
2. **Normalization:** Every scanner must output a standardized Python object (Pydantic).

## Base Interface
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class NormalizedFinding(BaseModel):
    title: str
    severity: str
    asset_identifier: str
    raw_evidence: str

class BaseScannerAdapter(ABC):
    @abstractmethod
    def build_command(self, target: str) -> list[str]:
        pass

    @abstractmethod
    def parse_output(self, raw_output: str) -> list[NormalizedFinding]:
        pass
```
"""

files["security_model.md"] = """# Security Model

## Boundaries & Constraints
1. **Authorized Scanning ONLY:** Scans can only be executed against strictly validated `Targets` associated with a `Project`. Arbitrary domain input bypassing the Project scope is rejected.
2. **No Exploitation:** Configuration for tools like Nuclei or OWASP ZAP will be strictly limited to `info`, `low`, `medium`, `high`, `critical` non-intrusive templates. Fuzzing is allowed; exploitation (e.g., dropping shells) is strictly forbidden.
3. **Secret Management:** API keys (e.g., for Subfinder) are injected via `.env` files and environment variables in Docker. They are never logged or stored in the DB in plaintext.
4. **RBAC:** Users can only view or scan projects they are explicitly assigned to.
"""

files["README.md"] = """# SentinelX (V1.0 Architecture)

Unified Attack Surface & Security Assessment Platform.

## Overview
SentinelX is a modular cybersecurity assessment platform designed for authorized security testing. It combines external attack-surface discovery, network/service discovery, and vulnerability intelligence into a single pane of glass.

## Stack
- **Frontend:** Next.js, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, SQLAlchemy
- **Async & Infrastructure:** Celery, Redis, PostgreSQL, Docker

## Documentation
Please refer to the architecture, database, and implementation markdown files in this directory for detailed design decisions.
"""

for filename, content in files.items():
    filepath = os.path.join(docs_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(files)} design documents in {docs_dir}/")
