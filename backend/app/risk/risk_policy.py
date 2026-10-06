POLICY_VERSION = "1.0"

RISK_WEIGHTS = {
    "kev_bonus": 1.5,
    "epss_multiplier": 2.0,
    "internet_exposure_bonus": 1.0,
    "service_exposure_bonus": 0.5
}

CRITICALITY_MULTIPLIERS = {
    "critical": 1.5,
    "high": 1.2,
    "medium": 1.0,
    "low": 0.8
}

CONFIDENCE_MULTIPLIERS = {
    "certain": 1.0,
    "high": 1.0,
    "medium": 0.9,
    "low": 0.8
}

def get_category(score: float) -> str:
    if score >= 9.0: return "Critical"
    if score >= 7.0: return "High"
    if score >= 4.0: return "Medium"
    if score > 0.0: return "Low"
    return "Informational"

def get_trend(delta: float) -> str:
    if delta > 0: return "increased"
    if delta < 0: return "decreased"
    return "unchanged"
