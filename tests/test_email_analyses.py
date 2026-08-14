import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.email_analysis import (
    AnalysisResult,
    CulturalRisk,
    EmailIntent,
    EmailRecommendation,
    LLMAnalysisResult,
    RiskSeverity,
    RiskType,
)
from app.services import analysis_service
from app.services.llm_service import LLMAnalysisError, LLMNotConfiguredError


client = TestClient(app)


@pytest.fixture
def cultural_analysis_result() -> LLMAnalysisResult:
    return LLMAnalysisResult(
        analysis=AnalysisResult(
            intent=EmailIntent.REVISION_REQUEST,
            request_summary="외부 협력사에 디자인 방향 수정을 요청",
            risk_score=85,
            risks=[
                CulturalRisk(
                    text="왜 이렇게 작업하셨는지 이해가 안 됩니다.",
                    type=RiskType.FACE_THREATENING_FEEDBACK,
                    severity=RiskSeverity.HIGH,
                    reason=(
                        "상대방의 판단 능력을 직접 비판하는 표현으로 "
                        "받아들여질 수 있습니다."
                    ),
                    suggestion=(
                        "요청 내용과 결과물 사이에 차이가 있었다는 방식으로 "
                        "설명하는 것이 좋습니다."
                    ),
                )
            ],
        ),
        recommendation=EmailRecommendation(
            subject="デザイン内容のご確認と修正のお願い",
            body="お世話になっております。修正をご検討いただけますでしょうか。",
        ),
    )


def test_create_email_analysis_returns_cultural_risk_and_recommendation(
    monkeypatch,
    cultural_analysis_result,
):
    monkeypatch.setattr(
        analysis_service,
        "analyze_email_with_llm",
        lambda request, recipient: cultural_analysis_result,
    )

    response = client.post(
        "/api/v1/email-analyses",
        json={
            "recipientEmail": "tanaka@abc.jp",
            "subject": "디자인 수정 요청",
            "body": (
                "보내주신 디자인은 저희가 요청한 방향과 많이 다릅니다. "
                "왜 이렇게 작업하셨는지 이해가 안 됩니다. "
                "다시 수정해서 보내주세요."
            ),
        },
    )

    assert response.status_code == 201
    result = response.json()
    assert result["analysisId"] == 1
    assert result["recipient"]["countryCode"] == "JP"
    assert result["recipient"]["relationship"] == "PARTNER"
    assert result["analysis"]["intent"] == "REVISION_REQUEST"
    assert result["analysis"]["riskScore"] == 85
    assert result["analysis"]["risks"][0]["type"] == (
        "FACE_THREATENING_FEEDBACK"
    )
    assert result["recommendation"]["subject"] == (
        "デザイン内容のご確認と修正のお願い"
    )
    assert result["createdAt"]


def test_get_email_analysis_returns_saved_detail(
    monkeypatch,
    cultural_analysis_result,
):
    monkeypatch.setattr(
        analysis_service,
        "analyze_email_with_llm",
        lambda request, recipient: cultural_analysis_result,
    )
    create_response = client.post(
        "/api/v1/email-analyses",
        json={
            "recipientEmail": "tanaka@abc.jp",
            "subject": "디자인 수정 요청",
            "body": "왜 이렇게 작업하셨는지 이해가 안 됩니다.",
        },
    )

    response = client.get(
        f"/api/v1/email-analyses/{create_response.json()['analysisId']}"
    )

    assert response.status_code == 200
    result = response.json()
    assert result["recipientEmail"] == "tanaka@abc.jp"
    assert result["originalSubject"] == "디자인 수정 요청"
    assert result["originalBody"] == "왜 이렇게 작업하셨는지 이해가 안 됩니다."
    assert result["riskResult"]["risks"][0]["type"] == (
        "FACE_THREATENING_FEEDBACK"
    )
    assert result["rewrittenSubject"] == "デザイン内容のご確認と修正のお願い"


def test_get_email_analysis_returns_404_for_unknown_id():
    response = client.get("/api/v1/email-analyses/999")

    assert response.status_code == 404
    assert response.json() == {
        "code": "EMAIL_ANALYSIS_NOT_FOUND",
        "message": "이메일 분석 결과를 찾을 수 없습니다.",
    }


def test_get_email_analyses_returns_newest_first(
    monkeypatch,
    cultural_analysis_result,
):
    monkeypatch.setattr(
        analysis_service,
        "analyze_email_with_llm",
        lambda request, recipient: cultural_analysis_result,
    )

    for subject in ["첫 번째 분석", "두 번째 분석"]:
        response = client.post(
            "/api/v1/email-analyses",
            json={
                "recipientEmail": "tanaka@abc.jp",
                "subject": subject,
                "body": "다시 수정해서 보내주세요.",
            },
        )
        assert response.status_code == 201

    response = client.get("/api/v1/email-analyses")

    assert response.status_code == 200
    assert [result["analysisId"] for result in response.json()] == [2, 1]
    assert [result["originalSubject"] for result in response.json()] == [
        "두 번째 분석",
        "첫 번째 분석",
    ]


def test_create_email_analysis_returns_404_for_unknown_recipient(monkeypatch):
    def fail_if_called(request, recipient):
        pytest.fail("LLM should not be called for an unknown recipient")

    monkeypatch.setattr(
        analysis_service,
        "analyze_email_with_llm",
        fail_if_called,
    )

    response = client.post(
        "/api/v1/email-analyses",
        json={
            "recipientEmail": "unknown@example.com",
            "subject": "Hello",
            "body": "Please review this design.",
        },
    )

    assert response.status_code == 404
    assert response.json()["code"] == "RECIPIENT_NOT_FOUND"


def test_create_email_analysis_returns_503_without_llm_configuration(monkeypatch):
    def raise_not_configured(request, recipient):
        raise LLMNotConfiguredError

    monkeypatch.setattr(
        analysis_service,
        "analyze_email_with_llm",
        raise_not_configured,
    )

    response = client.post(
        "/api/v1/email-analyses",
        json={
            "recipientEmail": "tanaka@abc.jp",
            "subject": "디자인 수정 요청",
            "body": "다시 수정해서 보내주세요.",
        },
    )

    assert response.status_code == 503
    assert response.json()["code"] == "LLM_NOT_CONFIGURED"


def test_create_email_analysis_returns_502_when_llm_fails(monkeypatch):
    def raise_analysis_error(request, recipient):
        raise LLMAnalysisError

    monkeypatch.setattr(
        analysis_service,
        "analyze_email_with_llm",
        raise_analysis_error,
    )

    response = client.post(
        "/api/v1/email-analyses",
        json={
            "recipientEmail": "tanaka@abc.jp",
            "subject": "디자인 수정 요청",
            "body": "다시 수정해서 보내주세요.",
        },
    )

    assert response.status_code == 502
    assert response.json()["code"] == "EMAIL_ANALYSIS_FAILED"


def test_create_email_analysis_returns_422_for_empty_body():
    response = client.post(
        "/api/v1/email-analyses",
        json={
            "recipientEmail": "tanaka@abc.jp",
            "subject": "디자인 수정 요청",
            "body": "",
        },
    )

    assert response.status_code == 422
