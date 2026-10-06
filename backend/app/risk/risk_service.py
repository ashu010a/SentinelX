from sqlalchemy.orm import Session
from sqlalchemy import desc
from .risk_engine import calculate_finding_risk
from .risk_models import FindingRiskInput
from .risk_policy import POLICY_VERSION, get_category, get_trend
import models

def save_risk_history(db: Session, entity_type: str, entity_id: str, project_id: str, result, previous_score: float = None):
    delta = round(result.score - previous_score, 1) if previous_score is not None else 0.0
    history = models.RiskHistory(
        entity_type=entity_type,
        entity_id=entity_id,
        project_id=project_id,
        score=result.score,
        previous_score=previous_score,
        delta=delta,
        trend=get_trend(delta),
        category=result.category,
        factors=result.factors,
        explanation=result.explanation,
        policy_version=result.policy_version
    )
    db.add(history)
    db.flush()
    return history

def process_finding_risk(db: Session, finding_id: str):
    finding = db.query(models.Finding).filter_by(id=finding_id).first()
    if not finding: return None
    asset = db.query(models.Asset).filter_by(id=finding.asset_id).first()
    
    inputs = FindingRiskInput(
        severity=finding.severity,
        cvss=finding.cvss,
        epss=finding.epss,
        kev=finding.kev,
        internet_exposed=getattr(asset, 'exposed', False),
        asset_criticality=getattr(asset, 'criticality', 'medium'),
        confidence=getattr(finding, 'confidence', 'certain')
    )
    
    result = calculate_finding_risk(inputs)
    
    # Get previous
    prev = db.query(models.RiskHistory).filter_by(entity_type="finding", entity_id=finding_id).order_by(desc(models.RiskHistory.calculated_at)).first()
    prev_score = prev.score if prev else None
    
    if prev_score != result.score or not prev:
        save_risk_history(db, "finding", finding_id, finding.project_id, result, prev_score)
        db.commit()
    return result

def calculate_project_risk(db: Session, project_id: str):
    # Overall Project Risk Calculation
    # based on highest asset risks
    asset_histories = db.query(models.RiskHistory).filter_by(project_id=project_id, entity_type="asset").order_by(desc(models.RiskHistory.calculated_at)).all()
    
    if not asset_histories: return None
    
    # Simple aggregate logic for demonstration
    scores = [h.score for h in asset_histories[:10]] # Latest 10 updates
    avg = sum(scores) / len(scores) if scores else 0.0
    
    from .risk_models import RiskResult
    result = RiskResult(
        score=round(avg, 1),
        category=get_category(avg),
        factors={"avg_asset_risk": round(avg, 1)},
        explanation="Project risk aggregated from underlying asset scores.",
        policy_version=POLICY_VERSION
    )
    
    prev = db.query(models.RiskHistory).filter_by(entity_type="project", entity_id=project_id).order_by(desc(models.RiskHistory.calculated_at)).first()
    save_risk_history(db, "project", project_id, project_id, result, prev.score if prev else None)
    db.commit()
    return result
