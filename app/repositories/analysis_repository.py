from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import EmailAnalysis
from app.schemas.email_analysis import (
    AnalysisRecipient,
    AnalysisResult,
    CulturalRisk,
    EmailAnalysisCreateRequest,
    EmailIntent,
    EmailRecommendation,
    LLMAnalysisResult,
)
from app.schemas.recipient import RecipientProfileResponse, Relationship


@dataclass(frozen=True)
class EmailAnalysisRecord:
    analysis_id: int
    recipient: AnalysisRecipient
    original_subject: str
    original_body: str
    analysis: AnalysisResult
    recommendation: EmailRecommendation
    created_at: datetime


def find_analysis_by_id(
    db: Session,
    analysis_id: int,
) -> EmailAnalysisRecord | None:
    analysis = db.scalar(
        select(EmailAnalysis)
        .options(joinedload(EmailAnalysis.recipient))
        .where(EmailAnalysis.id == analysis_id)
    )
    return _to_record(analysis) if analysis is not None else None


def find_all_analyses(db: Session) -> list[EmailAnalysisRecord]:
    analyses = db.scalars(
        select(EmailAnalysis)
        .options(joinedload(EmailAnalysis.recipient))
        .order_by(EmailAnalysis.id.desc())
    )
    return [_to_record(analysis) for analysis in analyses]


def save_analysis(
    db: Session,
    request: EmailAnalysisCreateRequest,
    recipient: RecipientProfileResponse,
    llm_result: LLMAnalysisResult,
) -> EmailAnalysisRecord:
    saved_analysis = EmailAnalysis(
        recipient_id=recipient.id,
        original_subject=request.subject,
        original_body=request.body,
        intent=llm_result.analysis.intent.value,
        request_summary=llm_result.analysis.request_summary,
        risk_score=llm_result.analysis.risk_score,
        risk_result={
            "risks": [
                risk.model_dump(mode="json")
                for risk in llm_result.analysis.risks
            ]
        },
        rewritten_subject=llm_result.recommendation.subject,
        rewritten_body=llm_result.recommendation.body,
        korean_rewritten_subject=llm_result.recommendation.korean_subject,
        korean_rewritten_body=llm_result.recommendation.korean_body,
    )
    db.add(saved_analysis)
    db.commit()
    db.refresh(saved_analysis)

    return EmailAnalysisRecord(
        analysis_id=saved_analysis.id,
        recipient=AnalysisRecipient(
            email=recipient.email,
            name=recipient.name,
            country_code=recipient.country_code,
            language_code=recipient.language_code,
            relationship=recipient.relationship,
            organization=recipient.organization,
        ),
        original_subject=saved_analysis.original_subject,
        original_body=saved_analysis.original_body,
        analysis=llm_result.analysis,
        recommendation=llm_result.recommendation,
        created_at=saved_analysis.created_at,
    )


def _to_record(analysis: EmailAnalysis) -> EmailAnalysisRecord:
    risks = [
        CulturalRisk.model_validate(risk)
        for risk in analysis.risk_result.get("risks", [])
    ]
    return EmailAnalysisRecord(
        analysis_id=analysis.id,
        recipient=AnalysisRecipient(
            email=analysis.recipient.email,
            name=analysis.recipient.name,
            country_code=analysis.recipient.country_code,
            language_code=analysis.recipient.language_code,
            relationship=Relationship(analysis.recipient.relationship_type),
            organization=analysis.recipient.organization,
        ),
        original_subject=analysis.original_subject,
        original_body=analysis.original_body,
        analysis=AnalysisResult(
            intent=EmailIntent(analysis.intent),
            request_summary=analysis.request_summary,
            risk_score=analysis.risk_score,
            risks=risks,
        ),
        recommendation=EmailRecommendation(
            subject=analysis.rewritten_subject,
            body=analysis.rewritten_body,
            korean_subject=analysis.korean_rewritten_subject or "",
            korean_body=analysis.korean_rewritten_body or "",
        ),
        created_at=analysis.created_at,
    )
