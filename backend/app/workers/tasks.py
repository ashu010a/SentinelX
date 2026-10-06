"""Celery tasks — scan pipeline execution.

This module contains the main scan pipeline task that orchestrates
the reconnaissance tools in sequence:

    subfinder → dnsx → httpx → naabu → nuclei

Each step calls the corresponding function in scanner_service,
normalizes the output, and persists it to PostgreSQL via a
synchronous SQLAlchemy session (Celery workers are synchronous).
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.asset import Asset
from app.models.endpoint import Endpoint
from app.models.scan_job import ScanJob
from app.models.service import Service
from app.models.vulnerability import Vulnerability
from app.services.scanner_service import (
    run_dnsx,
    run_httpx,
    run_naabu,
    run_nuclei,
    run_subfinder,
)
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

settings = get_settings()

# Synchronous engine for Celery (replace asyncpg with psycopg2)
sync_engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)
SyncSession = sessionmaker(bind=sync_engine)


def _update_scan(
    db: Session, scan_id: str, *, status: str | None = None,
    current_step: str | None = None, progress: int | None = None,
    error_message: str | None = None, results: dict | None = None,
) -> None:
    """Helper to update scan job status fields."""
    scan = db.query(ScanJob).filter(ScanJob.id == uuid.UUID(scan_id)).first()
    if not scan:
        return
    if status:
        scan.status = status
    if current_step is not None:
        scan.current_step = current_step
    if progress is not None:
        scan.progress = progress
    if error_message is not None:
        scan.error_message = error_message
    if results is not None:
        scan.results = results
    if status == "running" and scan.started_at is None:
        scan.started_at = datetime.now(timezone.utc)
    if status in ("completed", "failed"):
        scan.completed_at = datetime.now(timezone.utc)
    db.commit()


@celery_app.task(bind=True, name="sentinelx.run_scan")
def run_scan_pipeline(self, scan_job_id: str) -> dict:
    """Execute the full reconnaissance pipeline for a scan job.

    Pipeline steps:
        1. subfinder  — subdomain discovery      (20%)
        2. dnsx       — DNS resolution            (40%)
        3. httpx      — HTTP probing              (60%)
        4. naabu      — port scanning             (80%)
        5. nuclei     — vulnerability scanning    (100%)

    Results are saved to PostgreSQL after each step.
    """
    db = SyncSession()
    stats = {
        "subdomains": 0,
        "dns_resolved": 0,
        "http_endpoints": 0,
        "open_ports": 0,
        "vulnerabilities": 0,
    }

    try:
        # Get the scan job and project
        scan = db.query(ScanJob).filter(
            ScanJob.id == uuid.UUID(scan_job_id)
        ).first()
        if not scan:
            raise ValueError(f"Scan job {scan_job_id} not found")

        project_id = scan.project_id
        from app.models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        target = project.target
        logger.info("Starting scan pipeline for %s (job %s)", target, scan_job_id)

        _update_scan(db, scan_job_id, status="running", current_step="subfinder", progress=0)

        # ── Step 1: Subfinder ────────────────────────────────────────
        logger.info("[1/5] Running subfinder on %s", target)
        subdomains = run_subfinder(target)
        stats["subdomains"] = len(subdomains)
        logger.info("Discovered %d subdomains", len(subdomains))

        # Create or update Asset records for each subdomain
        asset_map: dict[str, Asset] = {}  # hostname → Asset
        for hostname in subdomains:
            existing = (
                db.query(Asset)
                .filter(Asset.project_id == project_id, Asset.hostname == hostname)
                .first()
            )
            if existing:
                existing.last_seen = datetime.now(timezone.utc)
                asset_map[hostname] = existing
            else:
                asset = Asset(
                    project_id=project_id,
                    hostname=hostname,
                    type="subdomain",
                    status="active",
                )
                db.add(asset)
                asset_map[hostname] = asset
        db.commit()

        _update_scan(db, scan_job_id, current_step="dnsx", progress=20)

        # ── Step 2: dnsx ─────────────────────────────────────────────
        logger.info("[2/5] Running dnsx on %d subdomains", len(subdomains))
        dns_results = run_dnsx(subdomains)
        stats["dns_resolved"] = len(dns_results)

        for record in dns_results:
            host = record.get("host", "")
            a_records = record.get("a", [])
            if host in asset_map and a_records:
                asset_map[host].ip = a_records[0]  # Primary IP
                asset_map[host].last_seen = datetime.now(timezone.utc)
        db.commit()

        _update_scan(db, scan_job_id, current_step="httpx", progress=40)

        # ── Step 3: httpx ────────────────────────────────────────────
        logger.info("[3/5] Running httpx on %d subdomains", len(subdomains))
        http_results = run_httpx(subdomains)
        stats["http_endpoints"] = len(http_results)

        for result in http_results:
            url = result.get("url", "")
            # Find matching asset by hostname
            input_host = result.get("input", "")
            host = result.get("host", input_host)

            asset = asset_map.get(host)
            if not asset:
                # Try to match by checking if any asset hostname is in the URL
                for h, a in asset_map.items():
                    if h in url:
                        asset = a
                        break
            if not asset:
                continue

            # Refresh the asset to get its id
            db.flush()

            endpoint = Endpoint(
                asset_id=asset.id,
                url=url,
                status_code=result.get("status_code") or result.get("status-code"),
                title=result.get("title", ""),
                content_type=result.get("content_type") or result.get("content-type", ""),
                content_length=result.get("content_length") or result.get("content-length"),
                technologies=result.get("tech") or result.get("technologies"),
            )
            db.add(endpoint)
        db.commit()

        _update_scan(db, scan_job_id, current_step="naabu", progress=60)

        # ── Step 4: naabu ────────────────────────────────────────────
        # Build host list — use IPs where available, else hostnames
        scan_hosts = []
        for hostname, asset in asset_map.items():
            scan_hosts.append(asset.ip if asset.ip else hostname)

        logger.info("[4/5] Running naabu on %d hosts", len(scan_hosts))
        port_results = run_naabu(scan_hosts)
        stats["open_ports"] = len(port_results)

        for result in port_results:
            host = result.get("host") or result.get("ip", "")
            port = result.get("port")
            if not port:
                continue

            # Find the asset by IP or hostname
            asset = None
            for h, a in asset_map.items():
                if a.ip == host or h == host:
                    asset = a
                    break
            if not asset:
                continue

            db.flush()

            # Avoid duplicates
            existing = (
                db.query(Service)
                .filter(Service.asset_id == asset.id, Service.port == port)
                .first()
            )
            if not existing:
                service = Service(
                    asset_id=asset.id,
                    port=port,
                    protocol=result.get("protocol", "tcp"),
                )
                db.add(service)
        db.commit()

        _update_scan(db, scan_job_id, current_step="nuclei", progress=80)

        # ── Step 5: nuclei ───────────────────────────────────────────
        # Build URL list from discovered endpoints
        endpoint_urls = []
        for hostname in asset_map:
            endpoint_urls.append(f"https://{hostname}")
            endpoint_urls.append(f"http://{hostname}")

        logger.info("[5/5] Running nuclei on %d URLs", len(endpoint_urls))
        vuln_results = run_nuclei(endpoint_urls)
        stats["vulnerabilities"] = len(vuln_results)

        for result in vuln_results:
            matched_at = result.get("matched-at", "")
            template_id = result.get("template-id", "")
            name = result.get("info", {}).get("name", template_id)
            severity = result.get("info", {}).get("severity", "info")

            # Find matching asset
            asset = None
            for h, a in asset_map.items():
                if h in matched_at:
                    asset = a
                    break
            if not asset:
                continue

            db.flush()

            # Extract CVE and other metadata from the result
            classification = result.get("info", {}).get("classification", {})
            cve_id = None
            if classification.get("cve-id"):
                cve_list = classification["cve-id"]
                cve_id = cve_list[0] if isinstance(cve_list, list) else cve_list

            cvss_score = None
            if classification.get("cvss-score"):
                try:
                    cvss_score = float(classification["cvss-score"])
                except (ValueError, TypeError):
                    pass

            vuln = Vulnerability(
                asset_id=asset.id,
                name=name,
                severity=severity.lower(),
                cve=cve_id,
                cvss=cvss_score,
                template_id=template_id,
                matcher_name=result.get("matcher-name", ""),
                evidence=result.get("extracted-results", str(result.get("matched-at", ""))),
                status="open",
            )
            db.add(vuln)
        db.commit()

        # ── Done ─────────────────────────────────────────────────────
        _update_scan(
            db, scan_job_id,
            status="completed",
            current_step="done",
            progress=100,
            results=stats,
        )
        logger.info("Scan pipeline completed for %s: %s", target, stats)
        return stats

    except Exception as exc:
        logger.exception("Scan pipeline failed for job %s", scan_job_id)
        _update_scan(
            db, scan_job_id,
            status="failed",
            error_message=str(exc),
            results=stats,
        )
        raise

    finally:
        db.close()
