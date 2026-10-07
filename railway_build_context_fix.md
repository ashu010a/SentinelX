# Railway Build Context Fix

## Root Cause of Previous Failure
The Railway deployment was failing during the `Railpack -> prepare -> Build Image` stage.
This occurred because the repository is a monorepo (`frontend/` and `backend/`). For a monorepo, Railway requires the **Root Directory** to be set to `/backend`.
When the root directory was set to `/backend`, Railway ignored the `railway.toml` file located at the repository root. Without that configuration file pointing to the Dockerfile, Railway looked for exactly `Dockerfile` in the `/backend` folder.
Because our file was named `Dockerfile.prod`, Railway did not find a Dockerfile, assumed the project was a standard Python app, and used **Railpack (Nixpacks)** to build it. Railpack subsequently failed to build the image because it lacked the system dependencies specified in our Dockerfile (like `libpq-dev`).

## Repository Structure Analysis
1. **Backend Application Location:** `/backend`
2. **Backend Dockerfile:** `/backend/Dockerfile.prod` (and `/backend/Dockerfile.worker` for the worker)
3. **Requirements Location:** `/backend/requirements.txt`
4. **FastAPI Entry Point:** `/backend/main.py`
5. **Monorepo:** Yes (frontend and backend in same repo)
6. **Correct Railway Root Directory:** `/backend`
7. **Docker Build Context:** `./backend`

## Changes Implemented
To fix this, we must configure Railway to use the correct Dockerfile while maintaining the `/backend` build context.

### Correct Railway Configuration
1. **Root Directory:** `/backend`
2. **Variable Injection:** `RAILWAY_DOCKERFILE_PATH=Dockerfile.prod`

By setting `RAILWAY_DOCKERFILE_PATH`, we explicitly tell Railway to use the Docker builder with `Dockerfile.prod`, bypassing the Railpack fallback.

### Dockerfile Path Corrections
Because the build context is now `/backend`, the `COPY` commands inside `Dockerfile.prod` and `Dockerfile.worker` must be relative to the `backend` directory itself. 

```dockerfile
# Reverted back to the context-aware paths
- COPY backend/requirements.txt .
+ COPY requirements.txt .

- COPY backend/ .
+ COPY . .
```

## Exact Local Build Command
If testing locally with Docker, the equivalent command matching Railway's new configuration is:
```bash
docker build -f backend/Dockerfile.prod ./backend
```

## Local Start Command
```bash
docker run -p 8000:8000 -e PORT=8000 sentinelx-api
```

## Files Changed
- `backend/Dockerfile.prod`
- `backend/Dockerfile.worker`
- `DEPLOYMENT.md`
- Deleted `railway.toml` from the repository root (as it causes conflicts in monorepo configurations).

## Verification Result
- Local Docker build context simulation confirms paths are correctly aligned with the `/backend` root.
- Python backend test suite (`run_rc1_checks.py`) executed successfully.
- Deployment documentation accurately reflects the required `RAILWAY_DOCKERFILE_PATH` variable.
