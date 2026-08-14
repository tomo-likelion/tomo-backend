from fastapi import APIRouter
from fastapi.responses import JSONResponse

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


router = APIRouter(prefix="/api/v1/recipients", tags=["recipients"])


@router.post(
    "",
    response_model=RecipientProfileResponse,
    status_code=201,
    responses={409: {"model": RecipientAlreadyExistsResponse}},
)
def register_recipient(
    request: RecipientCreateRequest,
) -> RecipientProfileResponse | JSONResponse:
    try:
        return create_recipient(request)
    except RecipientAlreadyExistsError:
        error = RecipientAlreadyExistsResponse()
        return JSONResponse(status_code=409, content=error.model_dump())


@router.get("", response_model=list[RecipientProfileResponse])
def get_recipients() -> list[RecipientProfileResponse]:
    return get_all_recipients()


@router.get(
    "/{email}",
    response_model=RecipientProfileResponse,
    responses={404: {"model": RecipientNotFoundResponse}},
)
def get_recipient(email: str) -> RecipientProfileResponse | JSONResponse:
    recipient = get_recipient_by_email(email)

    if recipient is None:
        error = RecipientNotFoundResponse()
        return JSONResponse(status_code=404, content=error.model_dump())

    return recipient
