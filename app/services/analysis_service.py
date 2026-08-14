from app.repositories.analysis_repository import (
    EmailAnalysisRecord,
    find_all_analyses,
    find_analysis_by_id,
    save_analysis,
)
from app.schemas.email_analysis import (
    AnalysisRiskResult,
    EmailAnalysisCreateRequest,
    EmailAnalysisCreateResponse,
    EmailAnalysisDetailResponse,
    EmailAnalysisSummaryResponse,
)
from app.services.llm_service import analyze_email_with_llm
from app.services.recipient_service import get_recipient_by_email


class AnalysisRecipientNotFoundError(Exception):
    pass


class EmailAnalysisNotFoundError(Exception):
    pass


def create_email_analysis(
    request: EmailAnalysisCreateRequest,
) -> EmailAnalysisCreateResponse:
    recipient = get_recipient_by_email(str(request.recipient_email))

    if recipient is None:
        raise AnalysisRecipientNotFoundError

    llm_result = analyze_email_with_llm(request, recipient)
    record = save_analysis(request, recipient, llm_result)

    return EmailAnalysisCreateResponse(
        analysis_id=record.analysis_id,
        recipient=record.recipient,
        analysis=record.analysis,
        recommendation=record.recommendation,
        created_at=record.created_at,
    )


def get_email_analysis(analysis_id: int) -> EmailAnalysisDetailResponse:
    record = find_analysis_by_id(analysis_id)

    if record is None:
        raise EmailAnalysisNotFoundError

    return _to_detail_response(record)


def get_email_analyses() -> list[EmailAnalysisSummaryResponse]:
    return [_to_summary_response(record) for record in find_all_analyses()]


def _to_detail_response(record: EmailAnalysisRecord) -> EmailAnalysisDetailResponse:
    return EmailAnalysisDetailResponse(
        analysis_id=record.analysis_id,
        recipient_email=record.recipient.email,
        original_subject=record.original_subject,
        original_body=record.original_body,
        intent=record.analysis.intent,
        request_summary=record.analysis.request_summary,
        risk_score=record.analysis.risk_score,
        risk_result=AnalysisRiskResult(risks=record.analysis.risks),
        rewritten_subject=record.recommendation.subject,
        rewritten_body=record.recommendation.body,
        created_at=record.created_at,
    )


def _to_summary_response(record: EmailAnalysisRecord) -> EmailAnalysisSummaryResponse:
    return EmailAnalysisSummaryResponse(
        analysis_id=record.analysis_id,
        recipient_email=record.recipient.email,
        original_subject=record.original_subject,
        intent=record.analysis.intent,
        risk_score=record.analysis.risk_score,
        created_at=record.created_at,
    )
