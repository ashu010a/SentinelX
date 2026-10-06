# Deployment Smoke Test
- [ ] **Frontend Load:** Verify Next.js renders cleanly on the Vercel domain.
- [ ] **Liveness Probe:** `GET https://[api-domain]/health` returns `200 OK`.
- [ ] **Readiness Probe:** `GET https://[api-domain]/ready` successfully queries Postgres.
- [ ] **Auth Check:** Secure cookies attach seamlessly across Vercel and Railway domains.
- [ ] **CORS Check:** API actively blocks requests from non-whitelisted origins.
