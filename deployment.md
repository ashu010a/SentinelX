# SentinelX Deployment Guide
## Target Architecture
- **Frontend:** Vercel (Next.js)
- **Backend:** Railway (FastAPI, Celery, PostgreSQL, Redis)

## 1. Database & Redis
Provision Managed PostgreSQL and Redis within a single Railway environment. This establishes your private network.

## 2. API Service
1. Connect Railway to your GitHub repository.
2. Go to Settings > Service > Root Directory and set it to `/backend`.
3. Go to Variables and add `RAILWAY_DOCKERFILE_PATH=Dockerfile.prod` (this forces Docker instead of Railpack).
4. Ensure `PORT` is bound automatically by Railway, overriding default `8000`.

## 3. Celery Worker
1. Duplicate the API service in Railway.
2. In Variables, change `RAILWAY_DOCKERFILE_PATH` to `Dockerfile.worker`.
3. In Settings, change the Custom Start Command to:
`celery -A main.celery_app worker --loglevel=info`

## 4. Frontend
1. Connect Vercel to your GitHub repository.
2. Set Root Directory to `frontend/`.
3. Define `NEXT_PUBLIC_API_URL` pointing to the generated Railway API domain.

## 5. Migrations
Execute `./scripts/migrate.sh` safely prior to application launch.
