from app.schemas.recipient import RecipientProfileResponse, Relationship


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
