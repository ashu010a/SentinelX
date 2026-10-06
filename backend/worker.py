import os
from database import SessionLocal
import models
from adapters import run_adapters

# Fallback synchronous executor for native testing environment
def execute_scan_sync(scan_job_id: str):
    db = SessionLocal()
    try:
        job = db.query(models.ScanJob).filter_by(id=scan_job_id).first()
        if not job: return
        job.status = "running"
        db.commit()

        target = db.query(models.Target).filter_by(id=job.target_id).first()
        results = run_adapters(target.target_value)
        
        asset_ids = []
        for d in results['domains']:
            asset = models.Asset(project_id=job.project_id, asset_type="domain", value=d['value'])
            db.add(asset)
            db.flush()
            asset_ids.append(asset.id)
            db.add(models.AssetChange(asset_id=asset.id, change_type='NEW ASSET'))
            
        if asset_ids:
            primary_asset = asset_ids[0]
            for v in results['vulns']:
                finding = models.Finding(project_id=job.project_id, asset_id=primary_asset, title=v['title'], severity=v['severity'], cvss=v['cvss'])
                db.add(finding)
                db.flush()
                db.add(models.AssetChange(asset_id=primary_asset, change_type='NEW VULNERABILITY'))
                db.add(models.RiskScore(asset_id=primary_asset, score=v['cvss'], reasons={"reasons": ["High exploit probability"]}))
                
        job.status = "completed"
        job.progress = 100
        db.commit()
    except Exception as e:
        db.rollback()
        if job:
            job.status = "failed"
            db.commit()
    finally:
        db.close()
