import sys
sys.path.append('backend')
from app.risk.risk_models import FindingRiskInput
from app.risk.risk_engine import calculate_finding_risk

print("--- Risk Engine Unit Tests ---")

# Test 1: Validation Rejection
try:
    calculate_finding_risk(FindingRiskInput(severity="high", cvss=11.0))
    print("FAIL: Accepted invalid CVSS")
    sys.exit(1)
except ValueError:
    print("PASS: Rejected invalid CVSS > 10")

# Test 2: Missing CVSS / Severity Fallback
res = calculate_finding_risk(FindingRiskInput(severity="medium"))
print(f"PASS: Missing CVSS mapped to Severity -> Score {res.score}")
assert res.score == 5.5

# Test 3: KEV & EPSS Modifiers
res = calculate_finding_risk(FindingRiskInput(severity="high", cvss=7.0, kev=True, epss=0.5))
print(f"PASS: KEV & EPSS correctly added -> Score {res.score}")
assert res.score == 9.5

# Test 4: Criticality Multiplier & Ceiling Cap
res = calculate_finding_risk(FindingRiskInput(severity="critical", cvss=9.0, internet_exposed=True, asset_criticality="critical"))
print(f"PASS: Score safely capped at 10.0 -> Score {res.score}")
assert res.score == 10.0

# Test 5: Explainability
print("Explanation Output:", res.explanation)
assert "Base score" in res.explanation
assert "internet-exposed" in res.explanation
assert "scaled by asset criticality multiplier (critical" in res.explanation

print("All Unit Tests Passed!")
