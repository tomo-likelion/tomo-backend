from app.repositories.recipient_repository import find_recipient_by_email
from app.schemas.recipient import RecipientProfileResponse


def get_recipient_by_email(email: str) -> RecipientProfileResponse | None:
    normalized_email = email.strip().lower()
    return find_recipient_by_email(normalized_email)
