# SentinelX Deployment Guide
## Target Architecture
- **Frontend:** Vercel (Next.js)
- **Backend:** Railway (FastAPI, Celery, PostgreSQL, Redis)

## 1. Database & Redis
Provision Managed PostgreSQL and Redis within a single Railway environment. This establishes your private network.

## 2. API Service
1. Connect Railway to your GitHub repository.
2. Set Root Directory to `/` (if monorepo) or `/backend`.
3. Railway will detect `railway.toml` and build via `backend/Dockerfile.prod`.
4. Ensure `PORT` is bound automatically by Railway, overriding default `8000`.

## 3. Celery Worker
Duplicate the API service in Railway. Change the Start Command to:
`celery -A main.celery_app worker --loglevel=info`

## 4. Frontend
1. Connect Vercel to your GitHub repository.
2. Set Root Directory to `frontend/`.
3. Define `NEXT_PUBLIC_API_URL` pointing to the generated Railway API domain.

## 5. Migrations
Execute `./scripts/migrate.sh` safely prior to application launch.
