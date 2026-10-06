# API Design

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
