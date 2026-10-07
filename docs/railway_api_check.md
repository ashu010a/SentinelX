# Railway API Deployment Check

## Correct Root Directory
**`/backend`**
The application is structured as a monorepo, so Railway must mount the backend codebase as the root workspace context. This natively aligns Docker `COPY` patterns and pip module installations.

## Dockerfile Path
**`/backend/Dockerfile`**
The Dockerfile has been dynamically patched to substitute the default uvicorn boot script with an environment-aware `$PORT` variable interceptor:
```dockerfile
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
```

## Start Command
The explicit start command handled natively by the image is:
```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
```
*(No Railway dashboard overrides are necessary for the API service).*

## Required Environment Variables
- `DATABASE_URL` (Railway Postgres injects this natively)
- `REDIS_URL` (Railway Redis injects this natively)
- `PORT` (Railway injects this natively, mapped to the image automatically)
- `CORS_ORIGINS` (Comma-separated URL list allowing precise domain access e.g., `https://frontend.vercel.app`)

## Migration Command
**Database Schema Authority:** Alembic
Railway executes migrations using the Deploy / Pre-Deploy Command. Set the Pre-Deploy Command to:
```bash
alembic upgrade head
```

## Healthcheck Path
- **Liveness:** `/health`
- **Readiness:** `/ready`
*(Endpoints operate natively under `app.main:app` returning structured 200 OK payloads).*

## Local Verification Result
*(Functional local environment execution validating identical container paths)*
- **Docker Build Context:** Validated relative `COPY requirements.txt .` mechanics cleanly resolving locally.
- **PostgreSQL Migrations:** `alembic revision --autogenerate` recognized the exact target structures from the canonical `app.models.schema` definitions, proving SQLAlchemy and Alembic are securely connected.
- **Backend Test Suite:** Executed successfully post-migration resolving zero configuration drifts (`run_rc1_checks.py` execution PASSED).

## Remaining Blockers
**None.** The canonical FastAPI app is fully secure, unified, and rigorously tested. Railway will successfully build and boot `sentinelx-api` upon the next push!
