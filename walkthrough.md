# Walkthrough
1. **Project Creation:** Verified via `POST /api/projects`.
2. **Target Creation:** Verified via `POST /api/projects/{id}/targets`.
3. **Scan Execution:** `POST /api/scans` triggered the pipeline. The Mock Adapters ran successfully.
4. **Data Normalization:** Raw scanner output was converted to 17-model schema records (Assets, Findings, RiskScores) in the database.
