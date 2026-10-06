# Risk Data Models
## `RiskHistory` Table
Enforces append-only immutable risk logging.
Never overwrites data. Fields:
- `score` & `previous_score` & `delta`
- `factors` (JSON representation of numeric modifiers)
- `explanation` (Human readable calculation steps)
- `policy_version`
