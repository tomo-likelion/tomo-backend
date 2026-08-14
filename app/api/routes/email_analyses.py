from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.email_analysis import (
    EmailAnalysisCreateRequest,
    EmailAnalysisCreateResponse,
    EmailAnalysisDetailResponse,
    EmailAnalysisFailedResponse,
    EmailAnalysisNotFoundResponse,
    EmailAnalysisSummaryResponse,
    LLMNotConfiguredResponse,
)
from app.schemas.recipient import RecipientNotFoundResponse
from app.services.analysis_service import (
    AnalysisRecipientNotFoundError,
    EmailAnalysisNotFoundError,
    create_email_analysis,
    get_email_analyses,
    get_email_analysis,
)
from app.services.llm_service import LLMAnalysisError, LLMNotConfiguredError


router = APIRouter(prefix="/api/v1/email-analyses", tags=["email-analyses"])


@router.post(
    "",
    response_model=EmailAnalysisCreateResponse,
    status_code=201,
    responses={
        404: {"model": RecipientNotFoundResponse},
        502: {"model": EmailAnalysisFailedResponse},
        503: {"model": LLMNotConfiguredResponse},
    },
)
def analyze_email(
    request: EmailAnalysisCreateRequest,
) -> EmailAnalysisCreateResponse | JSONResponse:
    try:
        return create_email_analysis(request)
    except AnalysisRecipientNotFoundError:
        error = RecipientNotFoundResponse()
        return JSONResponse(status_code=404, content=error.model_dump())
    except LLMNotConfiguredError:
        error = LLMNotConfiguredResponse()
        return JSONResponse(status_code=503, content=error.model_dump())
    except LLMAnalysisError:
        error = EmailAnalysisFailedResponse()
        return JSONResponse(status_code=502, content=error.model_dump())


@router.get("", response_model=list[EmailAnalysisSummaryResponse])
def list_email_analyses() -> list[EmailAnalysisSummaryResponse]:
    return get_email_analyses()


@router.get(
    "/{analysis_id}",
    response_model=EmailAnalysisDetailResponse,
    responses={404: {"model": EmailAnalysisNotFoundResponse}},
)
def get_email_analysis_by_id(
    analysis_id: int,
) -> EmailAnalysisDetailResponse | JSONResponse:
    try:
        return get_email_analysis(analysis_id)
    except EmailAnalysisNotFoundError:
        error = EmailAnalysisNotFoundResponse()
        return JSONResponse(status_code=404, content=error.model_dump())
