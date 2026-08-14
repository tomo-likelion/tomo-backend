from dataclasses import dataclass
from datetime import datetime, timezone

from app.schemas.email_analysis import (
    AnalysisRecipient,
    AnalysisResult,
    EmailAnalysisCreateRequest,
    EmailRecommendation,
    LLMAnalysisResult,
)
from app.schemas.recipient import RecipientProfileResponse


@dataclass(frozen=True)
class EmailAnalysisRecord:
    analysis_id: int
    recipient: AnalysisRecipient
    original_subject: str
    original_body: str
    analysis: AnalysisResult
    recommendation: EmailRecommendation
    created_at: datetime


_ANALYSES: dict[int, EmailAnalysisRecord] = {}


def save_analysis(
    request: EmailAnalysisCreateRequest,
    recipient: RecipientProfileResponse,
    llm_result: LLMAnalysisResult,
) -> EmailAnalysisRecord:
    analysis_id = max(_ANALYSES, default=0) + 1
    record = EmailAnalysisRecord(
        analysis_id=analysis_id,
        recipient=AnalysisRecipient(
            email=recipient.email,
            name=recipient.name,
            country_code=recipient.country_code,
            language_code=recipient.language_code,
            relationship=recipient.relationship,
            organization=recipient.organization,
        ),
        original_subject=request.subject,
        original_body=request.body,
        analysis=llm_result.analysis,
        recommendation=llm_result.recommendation,
        created_at=datetime.now(timezone.utc),
    )
    _ANALYSES[analysis_id] = record
    return record
