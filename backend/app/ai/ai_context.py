import re

SECRET_PATTERNS = [
    r'(?i)[a-z_]*(secret|key|token|password)[a-z_]*[\s:=]+([^\s]+)'
]

def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        # We need to replace the entire match or just the second group.
        # It's easier to just do a custom replace using a function
        def replacer(match):
            return match.group(0).replace(match.group(2), "[REDACTED]")
        redacted = re.sub(pattern, replacer, redacted)
    return redacted

def build_security_context(db, project_id: str, intent: str) -> str:
    raw_context = f"Project ID: {project_id}\\n"
    raw_context += "Active Findings: 2\\n"
    raw_context += "AWS_SECRET_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE\\n"
    
    safe_context = f"\\n--- UNTRUSTED SECURITY DATA START ---\\n{redact_secrets(raw_context)}\\n--- UNTRUSTED SECURITY DATA END ---\\n"
    return safe_context
