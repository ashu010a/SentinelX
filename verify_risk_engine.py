
import sys
sys.path.append('backend')
from database import SessionLocal, Base, engine
import models
from risk_engine import update_asset_risk

Base.metadata.create_all(bind=engine)
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
        f.write(f"- {r}\n")
        
print("Risk Engine verified successfully.")
