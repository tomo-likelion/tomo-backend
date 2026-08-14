from app.repositories.analysis_repository import save_analysis
from app.schemas.email_analysis import (
    EmailAnalysisCreateRequest,
    EmailAnalysisCreateResponse,
)
from app.services.llm_service import analyze_email_with_llm
from app.services.recipient_service import get_recipient_by_email


class AnalysisRecipientNotFoundError(Exception):
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
