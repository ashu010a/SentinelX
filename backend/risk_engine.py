
from sqlalchemy.orm import Session
import models

def calculate_finding_risk(cvss: float, epss: float, kev: bool, exposed: bool, criticality: str, confidence: str):
    reasons = []
    score = cvss or 0.0
    reasons.append(f"Base CVSS score established at {score}.")
    
    if kev:
        score += 2.0
        reasons.append("Critical increase: Vulnerability is actively exploited in the wild (CISA KEV).")
    
    if epss and epss > 0.5:
        score += 1.0
        reasons.append(f"High exploit probability (EPSS: {epss}).")
        
    if exposed:
        score += 1.0
        reasons.append("Risk elevated: The affected asset is internet-exposed.")
        
    crit_weights = {"low": 0.8, "medium": 1.0, "high": 1.2, "critical": 1.5}
    weight = crit_weights.get((criticality or "medium").lower(), 1.0)
    if weight != 1.0:
        score *= weight
        reasons.append(f"Score scaled by asset criticality multiplier ({criticality.upper()}).")
        
    conf_weights = {"low": 0.8, "medium": 0.9, "high": 1.0, "certain": 1.0}
    c_weight = conf_weights.get((confidence or "certain").lower(), 1.0)
    if c_weight != 1.0:
        score *= c_weight
        reasons.append(f"Score reduced due to lower scanner confidence ({confidence.upper()}).")
        
    final_score = min(round(score, 1), 10.0)
    return final_score, reasons

def update_asset_risk(asset_id: str, db: Session):
    asset = db.query(models.Asset).filter_by(id=asset_id).first()
    if not asset: return
    
    findings = db.query(models.Finding).filter_by(asset_id=asset_id).all()
    if not findings: return
    
    highest_score = 0.0
    highest_reasons = []
    
    for f in findings:
        score, reasons = calculate_finding_risk(
            cvss=f.cvss,
            epss=f.epss,
            kev=f.kev,
            exposed=asset.exposed,
            criticality=asset.criticality,
            confidence=f.confidence
        )
        if score > highest_score:
            highest_score = score
            highest_reasons = reasons
            highest_reasons.insert(0, f"Driven by finding: {f.title}")
            
    # Update or Create RiskScore record
    risk_record = db.query(models.RiskScore).filter_by(asset_id=asset_id).first()
    if not risk_record:
        risk_record = models.RiskScore(asset_id=asset_id)
        db.add(risk_record)
        
    risk_record.score = highest_score
    risk_record.reasons = {"reasons": highest_reasons}
    db.commit()
    return risk_record
