from app.schemas.email_analysis import CulturalRisk, RiskSeverity


_SEVERITY_RISK = {
    RiskSeverity.LOW: 0.15,
    RiskSeverity.MEDIUM: 0.35,
    RiskSeverity.HIGH: 0.65,
}


def calculate_risk_score(risks: list[CulturalRisk]) -> int:
    """Combine risk severities into a stable 0-100 cultural risk score."""
    remaining_safety = 1.0
    for risk in risks:
        remaining_safety *= 1 - _SEVERITY_RISK[risk.severity]

    return round((1 - remaining_safety) * 100)
