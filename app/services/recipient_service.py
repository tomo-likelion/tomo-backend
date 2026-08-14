from app.repositories.recipient_repository import (
    find_all_recipients,
    find_recipient_by_email,
    save_recipient,
)
from app.schemas.recipient import RecipientCreateRequest, RecipientProfileResponse


class RecipientAlreadyExistsError(Exception):
    pass


def get_recipient_by_email(email: str) -> RecipientProfileResponse | None:
    normalized_email = email.strip().lower()
    return find_recipient_by_email(normalized_email)


def get_all_recipients() -> list[RecipientProfileResponse]:
    return find_all_recipients()


def create_recipient(recipient: RecipientCreateRequest) -> RecipientProfileResponse:
    normalized_email = str(recipient.email).strip().lower()

    if find_recipient_by_email(normalized_email) is not None:
        raise RecipientAlreadyExistsError

    normalized_recipient = recipient.model_copy(update={"email": normalized_email})
    return save_recipient(normalized_recipient)
