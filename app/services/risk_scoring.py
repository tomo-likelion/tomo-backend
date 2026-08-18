from app.schemas.email_analysis import CulturalRisk, RiskSeverity


_SEVERITY_RISK = {
    RiskSeverity.LOW: 0.08,
    RiskSeverity.MEDIUM: 0.35,
    RiskSeverity.HIGH: 0.65,
}

_LOW_ONLY_SCORE_CAP = 30


def calculate_risk_score(risks: list[CulturalRisk]) -> int:
    """Combine risk severities into a stable 0-100 cultural risk score."""
    remaining_safety = 1.0
    for risk in risks:
        remaining_safety *= 1 - _SEVERITY_RISK[risk.severity]

    score = round((1 - remaining_safety) * 100)
    if risks and all(risk.severity == RiskSeverity.LOW for risk in risks):
        return min(score, _LOW_ONLY_SCORE_CAP)

    return score
