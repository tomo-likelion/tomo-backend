from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.email_analysis import (
    EmailAnalysisCreateRequest,
    EmailAnalysisCreateResponse,
    EmailAnalysisFailedResponse,
    LLMNotConfiguredResponse,
)
from app.schemas.recipient import RecipientNotFoundResponse
from app.services.analysis_service import (
    AnalysisRecipientNotFoundError,
    create_email_analysis,
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
