import pytest

from app.schemas.email_analysis import CulturalRisk, RiskSeverity, RiskType
from app.services.risk_scoring import (
    calculate_risk_score,
    normalize_risk_severities,
)


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


def test_obvious_rude_language_is_not_treated_as_low_risk():
    risks = [
        CulturalRisk(
            text="빨리좀해",
            type=RiskType.DIRECT_COMMAND,
            severity=RiskSeverity.LOW,
            reason="직접적인 명령입니다.",
            suggestion="정중하게 요청하세요.",
        ),
        CulturalRisk(
            text="빨리쫌해 짜증나니까",
            type=RiskType.FACE_THREATENING_FEEDBACK,
            severity=RiskSeverity.LOW,
            reason="감정적인 비난입니다.",
            suggestion="감정 표현을 제거하세요.",
        ),
        CulturalRisk(
            text="Subject: 빨리좀해",
            type=RiskType.AMBIGUOUS_DEADLINE,
            severity=RiskSeverity.LOW,
            reason="기한이 모호합니다.",
            suggestion="구체적인 일정을 요청하세요.",
        ),
    ]

    normalize_risk_severities(risks)

    assert [risk.severity for risk in risks] == [
        RiskSeverity.HIGH,
        RiskSeverity.HIGH,
        RiskSeverity.MEDIUM,
    ]
    assert calculate_risk_score(risks) == 92


def test_mild_low_risks_remain_low():
    risks = [
        CulturalRisk(
            text="the outstanding item",
            type=RiskType.FACE_THREATENING_FEEDBACK,
            severity=RiskSeverity.LOW,
            reason="표현이 다소 모호합니다.",
            suggestion="항목을 구체화하세요.",
        )
    ]

    normalize_risk_severities(risks)

    assert risks[0].severity == RiskSeverity.LOW
