from app.schemas.recipient import (
    RecipientCreateRequest,
    RecipientProfileResponse,
    Relationship,
)


_RECIPIENTS = {
    "tanaka@abc.jp": RecipientProfileResponse(
        id=1,
        email="tanaka@abc.jp",
        name="Tanaka",
        country_code="JP",
        language_code="ja",
        relationship=Relationship.PARTNER,
        organization="ABC Design",
    ),
    "alex@example.com": RecipientProfileResponse(
        id=2,
        email="alex@example.com",
        name="Alex",
        country_code="US",
        language_code="en",
        relationship=Relationship.CLIENT,
        organization="Example Inc.",
    ),
}


def find_recipient_by_email(email: str) -> RecipientProfileResponse | None:
    return _RECIPIENTS.get(email)


def find_all_recipients() -> list[RecipientProfileResponse]:
    return sorted(_RECIPIENTS.values(), key=lambda profile: profile.id)


def save_recipient(recipient: RecipientCreateRequest) -> RecipientProfileResponse:
    next_id = max(profile.id for profile in _RECIPIENTS.values()) + 1
    saved_recipient = RecipientProfileResponse(
        id=next_id,
        **recipient.model_dump(),
    )
    _RECIPIENTS[str(saved_recipient.email)] = saved_recipient
    return saved_recipient
