from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.recipient import (
    RecipientAlreadyExistsResponse,
    RecipientCreateRequest,
    RecipientNotFoundResponse,
    RecipientProfileResponse,
)
from app.services.recipient_service import (
    RecipientAlreadyExistsError,
    create_recipient,
    get_all_recipients,
    get_recipient_by_email,
)


router = APIRouter(prefix="/api/v1/recipients", tags=["수신자 관리"])


@router.post(
    "",
    summary="수신자 프로필 등록",
    description=(
        "이메일 분석에 사용할 수신자의 기본 정보와 관계 정보를 등록합니다. "
        "이미 등록된 이메일은 다시 등록할 수 없습니다."
    ),
    response_model=RecipientProfileResponse,
    status_code=201,
    response_description="등록된 수신자 프로필",
    responses={
        409: {
            "model": RecipientAlreadyExistsResponse,
            "description": "동일한 이메일의 수신자가 이미 등록되어 있음",
        },
    },
)
def register_recipient(
    request: RecipientCreateRequest,
    db: Session = Depends(get_db),
) -> RecipientProfileResponse | JSONResponse:
    try:
        return create_recipient(db, request)
    except RecipientAlreadyExistsError:
        error = RecipientAlreadyExistsResponse()
        return JSONResponse(status_code=409, content=error.model_dump())


@router.get(
    "",
    summary="수신자 목록 조회",
    description="현재 등록된 모든 수신자 프로필을 조회합니다.",
    response_model=list[RecipientProfileResponse],
    response_description="등록된 수신자 프로필 목록",
)
def get_recipients(
    db: Session = Depends(get_db),
) -> list[RecipientProfileResponse]:
    return get_all_recipients(db)


@router.get(
    "/{email}",
    summary="수신자 상세 조회",
    description="이메일 주소로 등록된 수신자 프로필을 조회합니다.",
    response_model=RecipientProfileResponse,
    response_description="조회된 수신자 프로필",
    responses={
        404: {
            "model": RecipientNotFoundResponse,
            "description": "해당 이메일로 등록된 수신자가 없음",
        },
    },
)
def get_recipient(
    email: str,
    db: Session = Depends(get_db),
) -> RecipientProfileResponse | JSONResponse:
    recipient = get_recipient_by_email(db, email)

    if recipient is None:
        error = RecipientNotFoundResponse()
        return JSONResponse(status_code=404, content=error.model_dump())

    return recipient
