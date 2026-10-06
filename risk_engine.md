# Risk Engine Architecture
## Overview
The SentinelX Risk Intelligence Engine translates raw scanner vulnerabilities into actionable, transparent business risk.

## Formula Design
- **Base:** Mapped to CVSS (0-10). If missing, gracefully falls back to scanner `Severity` string map.
- **Modifiers (+):** KEV (+1.5), EPSS (+ 2.0x), Internet Exposure (+1.0)
- **Multipliers (x):** Asset Criticality (Low: 0.8 to Critical: 1.5), Scanner Confidence (Low: 0.8 to Certain: 1.0)
- **Ceiling:** Hard limits mathematically restrict final scores between `0.0` and `10.0`.
