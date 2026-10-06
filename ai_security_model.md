# AI Security Model
- **Secret Redaction:** Regex pipeline strips high-entropy secrets and access keys from context before it leaves the backend.
- **Untrusted Data Boundaries:** All scanner output is strictly fenced inside `<UNTRUSTED SECURITY DATA>` XML tags in the prompt to structurally prevent injection.
- **Project Isolation:** Hard 403 checks prevent horizontal privilege escalation between project IDs.
