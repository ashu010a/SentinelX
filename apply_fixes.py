import re

file_path = "scaffold_mvp.py"
with open(file_path, "r") as f:
    content = f.read()

# Fix 1: Add index=True to all ForeignKeys for performance and to prevent table scans
content = re.sub(
    r'(Column\([^,]+,\s*ForeignKey\("[^"]+"\))(\))',
    r'\1, index=True\2',
    content
)

# Fix 2: Secure Dockerfile to run as non-root user
secure_dockerfile = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -s /bin/bash sentinelx && chown -R sentinelx:sentinelx /app
USER sentinelx
"""
content = re.sub(
    r'FROM python:3.11-slim.*?COPY \. \.\n',
    secure_dockerfile,
    content,
    flags=re.DOTALL
)

with open(file_path, "w") as f:
    f.write(content)

print("Applied security and performance fixes to scaffold_mvp.py")
