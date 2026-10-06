# System Architecture

## Overview
SentinelX follows a modular, async-driven architecture separating the API presentation layer from heavy security scanning workloads.

## Components
1. **Frontend (Next.js):** SSR/SSG capable React application using Tailwind and shadcn/ui.
2. **API Backend (FastAPI):** High-performance Python API handling routing, auth, and DB sessions.
3. **Task Queue (Celery + Redis):** Manages long-running security scans (Nmap, Nuclei) without blocking the API.
4. **Database (PostgreSQL):** Relational store for normalized findings, assets, and configurations.

## Architecture Diagram (Mermaid)
```mermaid
graph TD
    Client[Browser] -->|REST/HTTP| API[FastAPI Backend]
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Dispatch Job| Queue[(Redis)]
    Queue --> Worker[Celery Worker]
    Worker -->|Execute| Scanner[External Tool: Nmap, Nuclei, etc.]
    Scanner -->|Raw Output| Worker
    Worker -->|Normalize| DB
```

## Security Pipeline
Target -> Subfinder -> Dnsx -> Naabu/Nmap -> Httpx -> Nuclei -> Result Normalization -> DB
