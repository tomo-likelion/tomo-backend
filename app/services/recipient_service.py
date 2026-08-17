from sqlalchemy.orm import Session

from app.models.recipient_profile import RecipientProfile
from app.repositories.recipient_repository import (
    find_all_recipients,
    find_recipient_by_email,
    save_recipient,
)
from app.schemas.recipient import (
    RecipientCreateRequest,
    RecipientProfileResponse,
    Relationship,
)


class RecipientAlreadyExistsError(Exception):
    pass


def get_recipient_by_email(
    db: Session,
    email: str,
) -> RecipientProfileResponse | None:
    normalized_email = email.strip().lower()
    recipient = find_recipient_by_email(db, normalized_email)
    return _to_response(recipient) if recipient is not None else None


def get_all_recipients(db: Session) -> list[RecipientProfileResponse]:
    return [_to_response(recipient) for recipient in find_all_recipients(db)]


def create_recipient(
    db: Session,
    recipient: RecipientCreateRequest,
) -> RecipientProfileResponse:
    normalized_email = str(recipient.email).strip().lower()

    if find_recipient_by_email(db, normalized_email) is not None:
        raise RecipientAlreadyExistsError

    normalized_recipient = recipient.model_copy(update={"email": normalized_email})
    return _to_response(save_recipient(db, normalized_recipient))


def _to_response(recipient: RecipientProfile) -> RecipientProfileResponse:
    return RecipientProfileResponse(
        id=recipient.id,
        email=recipient.email,
        name=recipient.name,
        country_code=recipient.country_code,
        language_code=recipient.language_code,
        relationship=Relationship(recipient.relationship_type),
        organization=recipient.organization,
    )
