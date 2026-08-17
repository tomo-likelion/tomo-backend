from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
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


router = APIRouter(prefix="/api/v1/email-analyses", tags=["이메일 분석"])


@router.post(
    "",
    summary="이메일 문화적 맥락 분석",
    description=(
        "등록된 수신자의 국가, 언어 및 관계 정보를 바탕으로 이메일의 의도와 "
        "문화적 위험 요소를 분석하고, 수신자에게 적합하게 다듬은 제목과 본문을 "
        "추천합니다. 요청 전에 수신자 프로필이 등록되어 있어야 합니다."
    ),
    response_model=EmailAnalysisCreateResponse,
    status_code=201,
    response_description="분석 결과와 개선된 이메일 추천문",
    responses={
        404: {
            "model": RecipientNotFoundResponse,
            "description": "요청한 이메일의 수신자 프로필이 등록되어 있지 않음",
        },
        502: {
            "model": EmailAnalysisFailedResponse,
            "description": "외부 LLM 호출 또는 분석 처리에 실패함",
        },
        503: {
            "model": LLMNotConfiguredResponse,
            "description": "LLM API 키 등 분석에 필요한 환경 설정이 누락됨",
        },
    },
)
def analyze_email(
    request: EmailAnalysisCreateRequest,
    db: Session = Depends(get_db),
) -> EmailAnalysisCreateResponse | JSONResponse:
    try:
        return create_email_analysis(db, request)
    except AnalysisRecipientNotFoundError:
        error = RecipientNotFoundResponse()
        return JSONResponse(status_code=404, content=error.model_dump())
    except LLMNotConfiguredError:
        error = LLMNotConfiguredResponse()
        return JSONResponse(status_code=503, content=error.model_dump())
    except LLMAnalysisError:
        error = EmailAnalysisFailedResponse()
        return JSONResponse(status_code=502, content=error.model_dump())


@router.get(
    "",
    summary="이메일 분석 이력 목록 조회",
    description="저장된 이메일 분석 이력을 최신순으로 조회합니다.",
    response_model=list[EmailAnalysisSummaryResponse],
    response_description="이메일 분석 이력 요약 목록",
)
def list_email_analyses(
    db: Session = Depends(get_db),
) -> list[EmailAnalysisSummaryResponse]:
    return get_email_analyses(db)


@router.get(
    "/{analysis_id}",
    summary="이메일 분석 결과 상세 조회",
    description=(
        "분석 ID로 원본 이메일, 위험 요소, 위험 점수 및 추천 이메일을 포함한 "
        "분석 결과 전체를 조회합니다."
    ),
    response_model=EmailAnalysisDetailResponse,
    response_description="이메일 분석 상세 결과",
    responses={
        404: {
            "model": EmailAnalysisNotFoundResponse,
            "description": "해당 ID의 이메일 분석 결과가 없음",
        },
    },
)
def get_email_analysis_by_id(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> EmailAnalysisDetailResponse | JSONResponse:
    try:
        return get_email_analysis(db, analysis_id)
    except EmailAnalysisNotFoundError:
        error = EmailAnalysisNotFoundResponse()
        return JSONResponse(status_code=404, content=error.model_dump())
