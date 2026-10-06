FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -s /bin/bash sentinelx && chown -R sentinelx:sentinelx /app
USER sentinelx
