from .risk_policy import POLICY_VERSION, RISK_WEIGHTS, CRITICALITY_MULTIPLIERS, CONFIDENCE_MULTIPLIERS, get_category
from .risk_models import FindingRiskInput, RiskResult

def calculate_finding_risk(inputs: FindingRiskInput) -> RiskResult:
    # Validation
    if inputs.cvss is not None and (inputs.cvss < 0 or inputs.cvss > 10):
        raise ValueError("CVSS must be between 0 and 10")
    if inputs.epss is not None and (inputs.epss < 0 or inputs.epss > 1):
        raise ValueError("EPSS must be between 0 and 1")

    factors = {}
    explanations = []
    
    # 1. Base Score
    if inputs.cvss and inputs.cvss > 0:
        base = inputs.cvss
        factors['CVSS'] = base
    else:
        sev_map = {"critical": 9.5, "high": 7.5, "medium": 5.5, "low": 2.5, "info": 0.0}
        base = sev_map.get(inputs.severity.lower(), 0.0)
        factors['Severity Fallback'] = base
        
    score = base
    explanations.append(f"Base score established at {base:.1f}.")

    # 2. Additive Modifiers
    if inputs.kev:
        val = RISK_WEIGHTS['kev_bonus']
        score += val
        factors['KEV'] = val
        explanations.append("Increased due to Known Exploited Vulnerability status (+1.5).")
        
    if inputs.epss and inputs.epss > 0:
        val = round(inputs.epss * RISK_WEIGHTS['epss_multiplier'], 2)
        score += val
        factors['EPSS'] = val
        explanations.append(f"Increased due to EPSS probability of {inputs.epss} (+{val}).")
        
    if inputs.internet_exposed:
        val = RISK_WEIGHTS['internet_exposure_bonus']
        score += val
        factors['Internet Exposure'] = val
        explanations.append("Risk elevated: Asset is internet-exposed (+1.0).")

    # 3. Multiplicative Modifiers
    crit_mult = CRITICALITY_MULTIPLIERS.get(inputs.asset_criticality.lower(), 1.0)
    if crit_mult != 1.0:
        score *= crit_mult
        factors['Asset Criticality'] = crit_mult
        explanations.append(f"Score scaled by asset criticality multiplier ({inputs.asset_criticality}: x{crit_mult}).")

    conf_mult = CONFIDENCE_MULTIPLIERS.get(inputs.confidence.lower(), 1.0)
    if conf_mult != 1.0:
        score *= conf_mult
        factors['Confidence'] = conf_mult
        explanations.append(f"Score scaled by scanner confidence ({inputs.confidence}: x{conf_mult}).")

    # Finalize
    final_score = min(round(score, 1), 10.0)
    final_score = max(final_score, 0.0)
    
    return RiskResult(
        score=final_score,
        category=get_category(final_score),
        factors=factors,
        explanation=" ".join(explanations),
        policy_version=POLICY_VERSION
    )
