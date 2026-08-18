from app.schemas.email_analysis import (
    CulturalRisk,
    RiskSeverity,
    RiskType,
)


_SEVERITY_RISK = {
    RiskSeverity.LOW: 0.08,
    RiskSeverity.MEDIUM: 0.35,
    RiskSeverity.HIGH: 0.65,
}

_LOW_ONLY_SCORE_CAP = 30

_SEVERITY_RANK = {
    RiskSeverity.LOW: 1,
    RiskSeverity.MEDIUM: 2,
    RiskSeverity.HIGH: 3,
}

_STRONG_URGENCY_MARKERS = (
    "당장",
    "빨리",
    "즉시",
    "지금 바로",
    "오늘 안",
    "asap",
    "immediately",
    "right now",
)

_STRONG_NEGATIVE_MARKERS = (
    "짜증",
    "화나",
    "열받",
    "답답",
    "이해가 안",
    "왜 이렇게",
    "무능",
    "실망",
    "annoy",
    "frustrat",
    "ridiculous",
    "unacceptable",
    "stupid",
    "your fault",
)


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    normalized_text = text.casefold()
    return any(marker in normalized_text for marker in markers)


def _raise_severity(risk: CulturalRisk, minimum: RiskSeverity) -> None:
    if _SEVERITY_RANK[risk.severity] < _SEVERITY_RANK[minimum]:
        risk.severity = minimum


def normalize_risk_severities(risks: list[CulturalRisk]) -> None:
    """Correct clearly understated LLM severities before score calculation."""
    for risk in risks:
        has_strong_urgency = _contains_marker(
            risk.text,
            _STRONG_URGENCY_MARKERS,
        )
        has_strong_negative = _contains_marker(
            risk.text,
            _STRONG_NEGATIVE_MARKERS,
        )

        if risk.type == RiskType.DIRECT_COMMAND:
            minimum = (
                RiskSeverity.HIGH
                if has_strong_urgency
                else RiskSeverity.MEDIUM
            )
            _raise_severity(risk, minimum)
        elif (
            risk.type == RiskType.FACE_THREATENING_FEEDBACK
            and has_strong_negative
        ):
            _raise_severity(risk, RiskSeverity.HIGH)
        elif (
            risk.type == RiskType.AMBIGUOUS_DEADLINE
            and has_strong_urgency
        ):
            _raise_severity(risk, RiskSeverity.MEDIUM)
        elif risk.type == RiskType.RELATIONSHIP_MISMATCH:
            _raise_severity(risk, RiskSeverity.MEDIUM)


def calculate_risk_score(risks: list[CulturalRisk]) -> int:
    """Combine risk severities into a stable 0-100 cultural risk score."""
    remaining_safety = 1.0
    for risk in risks:
        remaining_safety *= 1 - _SEVERITY_RISK[risk.severity]

    score = round((1 - remaining_safety) * 100)
    if risks and all(risk.severity == RiskSeverity.LOW for risk in risks):
        return min(score, _LOW_ONLY_SCORE_CAP)

    return score
