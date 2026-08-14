from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.recipient import (
    RecipientNotFoundResponse,
    RecipientProfileResponse,
)
from app.services.recipient_service import get_recipient_by_email


router = APIRouter(prefix="/api/v1/recipients", tags=["recipients"])


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
