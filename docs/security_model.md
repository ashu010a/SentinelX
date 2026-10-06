# Security Model

## Boundaries & Constraints
1. **Authorized Scanning ONLY:** Scans can only be executed against strictly validated `Targets` associated with a `Project`. Arbitrary domain input bypassing the Project scope is rejected.
2. **No Exploitation:** Configuration for tools like Nuclei or OWASP ZAP will be strictly limited to `info`, `low`, `medium`, `high`, `critical` non-intrusive templates. Fuzzing is allowed; exploitation (e.g., dropping shells) is strictly forbidden.
3. **Secret Management:** API keys (e.g., for Subfinder) are injected via `.env` files and environment variables in Docker. They are never logged or stored in the DB in plaintext.
4. **RBAC:** Users can only view or scan projects they are explicitly assigned to.
