import socket
import uuid
import urllib.request
from sqlalchemy.orm import Session
from app.models import schema as models

def perform_scan(scan_job_id: str, project_id: str, target: str, db: Session):
    try:
        # 1. Update scan status to running
        scan = db.query(models.ScanJob).filter(models.ScanJob.id == scan_job_id).first()
        if scan:
            scan.status = "running"
            scan.progress = 10
            db.commit()

        # Clean target (remove http:// or paths)
        clean_target = target.replace("http://", "").replace("https://", "").split("/")[0]
        
        # 2. OPERATION 1: DNS Resolution / Asset Discovery
        ip_address = None
        asset_id = None
        try:
            ip_address = socket.gethostbyname(clean_target)
            asset_id = str(uuid.uuid4())
            asset = models.Asset(
                id=asset_id,
                project_id=project_id,
                hostname=clean_target,
                ip=ip_address,
                type="web_server",
                risk_score=45.0
            )
            db.add(asset)
            db.commit()
            if scan:
                scan.progress = 50
                db.commit()
        except Exception as e:
            print(f"DNS Resolution failed for {clean_target}: {e}")

        # 3. OPERATION 2: Basic Vulnerability Check (Security Headers)
        if asset_id:
            try:
                req = urllib.request.Request(f"http://{clean_target}")
                with urllib.request.urlopen(req, timeout=5) as response:
                    headers = response.headers
                    if 'X-Frame-Options' not in headers:
                        vuln = models.Vulnerability(
                            id=str(uuid.uuid4()),
                            asset_id=asset_id,
                            name="Missing X-Frame-Options Header",
                            severity="medium",
                            status="open"
                        )
                        db.add(vuln)
                        db.commit()
            except Exception as e:
                print(f"HTTP Check failed for {clean_target}: {e}")

        # 4. Mark scan as complete
        if scan:
            scan.status = "completed"
            scan.progress = 100
            db.commit()
            
    except Exception as e:
        if scan:
            scan.status = "failed"
            db.commit()
        print(f"Scan critical failure: {e}")
    finally:
        db.close()
