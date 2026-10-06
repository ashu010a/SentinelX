# Security Audit

## 1. Docker & Infrastructure Security
**Status:** FIXED
**Vulnerability:** *Insecure Docker Configuration (Root Execution)*
**Details:** The generated backend `Dockerfile` did not specify a user, meaning the FastAPI application and Celery workers would run as `root` inside the container.
**Remediation:** Modified the Dockerfile to create and switch to a non-privileged `sentinelx` user before execution.

## 2. Injection Flaws (SQLi & Command Injection)
**Status:** PASS
**Details:** 
- **SQLi:** Standard use of SQLAlchemy ORM prevents SQL injection. No raw string interpolation is used for queries.
- **Command Injection:** The mock adapters do not currently execute shell commands. *Warning for Future Impl:* When `subprocess` is introduced for tools like Nmap, the `BaseScannerAdapter` must enforce list-based execution (`subprocess.run(["nmap", target])`) rather than shell execution (`shell=True`) to prevent arbitrary command injection.

## 3. Server-Side Request Forgery (SSRF)
**Status:** ARCHITECTURAL WARNING
**Details:** Future adapters (like HTTPX or ZAP) will make outbound requests to user-supplied targets. Without a target validation layer, a malicious user could supply `169.254.169.254` or `localhost` to scan internal cloud metadata or backend services. 
**Remediation Plan:** A strict validation interceptor must be added to `validate_target()` that rejects reserved, private, and loopback IP spaces before the Celery worker triggers the scanner.

## 4. Tenant Isolation & IDOR
**Status:** ARCHITECTURAL WARNING
**Details:** Because authentication was excluded from the MVP phase per instructions, endpoints like `/api/projects/{id}/assets` do not strictly verify that the requesting user *owns* the project ID. 
**Remediation Plan:** Once the Auth layer is fully implemented, all endpoints must transition from `Depends(get_db)` to a dependency that inherently enforces project ownership (`Depends(get_authorized_project)`).

## 5. Secret Leakage
**Status:** PASS
**Details:** API credentials and database URIs are correctly sourced from environment variables (`os.getenv`), preventing hardcoded secrets in the repository.
