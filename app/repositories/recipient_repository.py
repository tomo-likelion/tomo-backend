from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RecipientProfile
from app.schemas.recipient import RecipientCreateRequest


def find_recipient_by_email(
    db: Session,
    email: str,
) -> RecipientProfile | None:
    return db.scalar(
        select(RecipientProfile).where(RecipientProfile.email == email)
    )


def find_all_recipients(db: Session) -> list[RecipientProfile]:
    return list(
        db.scalars(select(RecipientProfile).order_by(RecipientProfile.id))
    )


def save_recipient(
    db: Session,
    recipient: RecipientCreateRequest,
) -> RecipientProfile:
    saved_recipient = RecipientProfile(
        email=str(recipient.email),
        name=recipient.name,
        country_code=recipient.country_code,
        language_code=recipient.language_code,
        relationship_type=recipient.relationship.value,
        organization=recipient.organization,
    )
    db.add(saved_recipient)
    db.commit()
    db.refresh(saved_recipient)
    return saved_recipient
