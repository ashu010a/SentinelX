# Risk Engine Validation Results

## Test Execution
- **Target Asset:** `payment.example.com` (Criticality: HIGH, Exposed: TRUE)
- **Top Finding:** Zero-Day Remote Code Execution (CVSS: 7.5, KEV: TRUE, EPSS: 0.8)

## Engine Output
**Final Score:** 10.0 / 10.0

**Reasoning Matrix:**
- Driven by finding: Zero-Day Remote Code Execution
- Base CVSS score established at 7.5.
- Critical increase: Vulnerability is actively exploited in the wild (CISA KEV).
- High exploit probability (EPSS: 0.8).
- Risk elevated: The affected asset is internet-exposed.
- Score scaled by asset criticality multiplier (HIGH).
