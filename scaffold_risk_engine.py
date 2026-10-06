import os
import sqlite3

print("Starting Risk Engine implementation...")

# 1. Patch the Database Schema (Adding new columns for the Risk Engine)
db_path = "backend/sentinelx_mvp.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE assets ADD COLUMN criticality VARCHAR DEFAULT 'medium'")
        cur.execute("ALTER TABLE assets ADD COLUMN exposed BOOLEAN DEFAULT 0")
        cur.execute("ALTER TABLE findings ADD COLUMN confidence VARCHAR DEFAULT 'certain'")
        conn.commit()
        print("Patched database schema with criticality, exposed, and confidence fields.")
    except Exception as e:
        print("Schema already patched or error:", e)
    conn.close()

# 2. Update models.py to reflect the new schema
with open("backend/models.py", "r") as f:
    models_code = f.read()

if "criticality = Column(String" not in models_code:
    models_code = models_code.replace(
        "is_live = Column(Boolean, default=True)",
        "is_live = Column(Boolean, default=True)\n    criticality = Column(String, default='medium')\n    exposed = Column(Boolean, default=False)"
    )
    models_code = models_code.replace(
        "kev = Column(Boolean, default=False)",
        "kev = Column(Boolean, default=False)\n    confidence = Column(String, default='certain')"
    )
    with open("backend/models.py", "w") as f:
        f.write(models_code)
        
# 3. Create the Risk Engine module
with open("backend/risk_engine.py", "w") as f:
    f.write("""
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
""")

# 4. Create a test script for the Risk Engine
with open("verify_risk_engine.py", "w") as f:
    f.write("""
import sys
sys.path.append('backend')
from database import SessionLocal, Base, engine
import models
from risk_engine import update_asset_risk

db = SessionLocal()

print("--- Testing Risk Engine ---")

# 1. Setup Mock Data
project = models.Project(name="Risk Engine Test")
db.add(project)
db.commit()

# Create a Highly Critical, Internet-Exposed Asset
asset = models.Asset(
    project_id=project.id, 
    asset_type="domain", 
    value="payment.example.com",
    criticality="high",
    exposed=True
)
db.add(asset)
db.commit()

# Add a standard Finding (e.g. CVSS 5.0, not KEV)
finding1 = models.Finding(
    project_id=project.id,
    asset_id=asset.id,
    title="Standard Misconfiguration",
    severity="medium",
    cvss=5.0,
    kev=False,
    epss=0.1,
    confidence="certain"
)

# Add a severe Finding (CVSS 7.5, KEV=True, High EPSS)
finding2 = models.Finding(
    project_id=project.id,
    asset_id=asset.id,
    title="Zero-Day Remote Code Execution",
    severity="critical",
    cvss=7.5,
    kev=True,
    epss=0.8,
    confidence="certain"
)

db.add_all([finding1, finding2])
db.commit()

# 2. Execute Risk Engine
print("Calculating compound risk score...")
risk_record = update_asset_risk(asset.id, db)

# 3. Output Results
print(f"Final Computed Asset Risk Score: {risk_record.score} / 10.0")
print("Calculation Logic:")
for reason in risk_record.reasons['reasons']:
    print(f" - {reason}")

# 4. Assertions
# Expected for finding2: 
# Base CVSS = 7.5
# KEV (+2.0) = 9.5
# EPSS > 0.5 (+1.0) = 10.5
# Exposed (+1.0) = 11.5
# Criticality High (*1.2) = 13.8 -> Maxed to 10.0
assert risk_record.score == 10.0, "Risk score did not cap at 10.0 or calculate correctly"

with open("risk_engine_test_results.md", "w") as f:
    f.write(f'''# Risk Engine Validation Results

## Test Execution
- **Target Asset:** `payment.example.com` (Criticality: HIGH, Exposed: TRUE)
- **Top Finding:** Zero-Day Remote Code Execution (CVSS: 7.5, KEV: TRUE, EPSS: 0.8)

## Engine Output
**Final Score:** {risk_record.score} / 10.0

**Reasoning Matrix:**
''')
    for r in risk_record.reasons['reasons']:
        f.write(f"- {r}\\n")
        
print("Risk Engine verified successfully.")
""")
print("Scaffolding complete.")
