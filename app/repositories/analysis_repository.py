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


def find_analysis_by_id(analysis_id: int) -> EmailAnalysisRecord | None:
    return _ANALYSES.get(analysis_id)


def find_all_analyses() -> list[EmailAnalysisRecord]:
    return sorted(
        _ANALYSES.values(),
        key=lambda record: record.analysis_id,
        reverse=True,
    )


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
