from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import models
from .correlation_rules import RULES

def generate_fingerprint(project_id: str, asset_id: str, title: str) -> str:
    raw = f"{project_id}:{asset_id}:{title}".encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def deduplicate_finding(db: Session, finding: models.Finding, scanner_name: str) -> models.Finding:
    fp = generate_fingerprint(finding.project_id, finding.asset_id, finding.title)
    existing = db.query(models.Finding).filter_by(fingerprint=fp).first()
    
    if existing:
        existing.occurrence_count += 1
        existing.last_seen = datetime.utcnow()
        if scanner_name not in (existing.scanner_sources or ""):
            existing.scanner_sources = f"{existing.scanner_sources or ''},{scanner_name}".strip(",")
        db.commit()
        return existing
    
    finding.fingerprint = fp
    finding.scanner_sources = scanner_name
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding

def run_correlation_engine(project_id: str, db: Session):
    for rule in RULES:
        links = rule.evaluate(project_id, db)
        for link in links:
            # Upsert
            existing = db.query(models.Relationship).filter_by(
                source_id=link['source_id'], 
                target_id=link['target_id'], 
                relationship_type=link['type']
            ).first()
            if existing:
                existing.last_seen = datetime.utcnow()
                existing.explanation = link['explanation']
                existing.confidence = link['confidence']
            else:
                rel = models.Relationship(
                    project_id=project_id,
                    source_id=link['source_id'],
                    target_id=link['target_id'],
                    relationship_type=link['type'],
                    confidence=link['confidence'],
                    explanation=link['explanation']
                )
                db.add(rel)
    db.commit()
