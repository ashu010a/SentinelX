import os

with open('DEPLOYMENT.md', 'r') as f:
    content = f.read()

content = content.replace(
    '2. Set Root Directory to `/` (if monorepo) or `/backend`.\n3. Railway will detect `railway.toml` and build via `backend/Dockerfile.prod`.',
    '2. Go to Settings > Service > Root Directory and set it to `/backend`.\n3. Go to Variables and add `RAILWAY_DOCKERFILE_PATH=Dockerfile.prod` (this forces Docker instead of Railpack).'
)

content = content.replace(
    '## 3. Celery Worker\nDuplicate the API service in Railway. Change the Start Command to:\n`celery -A main.celery_app worker --loglevel=info`',
    '## 3. Celery Worker\n1. Duplicate the API service in Railway.\n2. In Variables, change `RAILWAY_DOCKERFILE_PATH` to `Dockerfile.worker`.\n3. In Settings, change the Custom Start Command to:\n`celery -A main.celery_app worker --loglevel=info`'
)

with open('DEPLOYMENT.md', 'w') as f:
    f.write(content)
