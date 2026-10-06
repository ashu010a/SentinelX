# Deployment Audit
**Blockers Identified & Fixed:**
- *Static CORS:* Replaced wildcard origins with dynamic `CORS_ORIGINS` environment variables.
- *Health Probes:* Missing Liveness/Readiness probes added natively (`/health`, `/ready`).
- *Ephemeral Storage:* Acknowledged that Railway destroys local files on redeploy. Implemented `StorageProvider` abstraction for future S3 integration to safeguard generated reports.
