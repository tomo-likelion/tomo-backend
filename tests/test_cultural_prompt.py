from app.prompts.cultural_prompt import SYSTEM_PROMPT, build_analysis_prompt
from app.schemas.email_analysis import EmailAnalysisCreateRequest
from app.schemas.recipient import RecipientProfileResponse, Relationship


def test_prompt_separates_analysis_and_recommendation_languages():
    request = EmailAnalysisCreateRequest(
        recipientEmail="tanaka@abc.jp",
        subject="디자인 수정 요청",
        body="디자인을 다시 수정해서 보내주세요.",
    )
    recipient = RecipientProfileResponse(
        id=1,
        email="tanaka@abc.jp",
        name="Tanaka",
        countryCode="JP",
        languageCode="ja",
        relationship=Relationship.PARTNER,
        organization="ABC Design",
    )

    prompt = build_analysis_prompt(request, recipient)

    assert "every risk reason and suggestion in Korean" in SYSTEM_PROMPT
    assert "Only the recommended email subject" in SYSTEM_PROMPT
    assert "riskScore field means cultural misunderstanding risk" in SYSTEM_PROMPT
    assert "0 means no detected risk" in SYSTEM_PROMPT
    assert "100 means" in SYSTEM_PROMPT
    assert "extreme risk" in SYSTEM_PROMPT
    assert "complete and ready to send" in SYSTEM_PROMPT
    assert "Do not include" in SYSTEM_PROMPT
    assert "bracketed placeholders" in SYSTEM_PROMPT
    assert "no HIGH or MEDIUM cultural risks" in SYSTEM_PROMPT
    assert "riskScore of 30 or lower" in SYSTEM_PROMPT
    assert "analysis explanations in Korean" in prompt
    assert "localized subject and body in ja" in prompt
