import pytest

from app.schemas.email_analysis import CulturalRisk, RiskSeverity, RiskType
from app.services.risk_scoring import calculate_risk_score


def make_risk(severity: RiskSeverity) -> CulturalRisk:
    return CulturalRisk(
        text="테스트 표현",
        type=RiskType.CULTURAL_TONE,
        severity=severity,
        reason="테스트 사유",
        suggestion="테스트 제안",
    )


@pytest.mark.parametrize(
    ("severity", "expected_score"),
    [
        (RiskSeverity.LOW, 8),
        (RiskSeverity.MEDIUM, 35),
        (RiskSeverity.HIGH, 65),
    ],
)
def test_single_risk_score_uses_severity_weight(severity, expected_score):
    assert calculate_risk_score([make_risk(severity)]) == expected_score


def test_no_risks_has_zero_score():
    assert calculate_risk_score([]) == 0


def test_multiple_risks_accumulate_with_diminishing_returns():
    risks = [
        make_risk(RiskSeverity.HIGH),
        make_risk(RiskSeverity.MEDIUM),
        make_risk(RiskSeverity.MEDIUM),
    ]

    assert calculate_risk_score(risks) == 85


def test_low_only_risks_keep_acceptance_score_at_least_seventy():
    risks = [make_risk(RiskSeverity.LOW) for _ in range(10)]

    assert calculate_risk_score(risks) == 30
