from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import RecipientProfile


RECIPIENTS = [
    {
        "email": "tanaka@abc.jp",
        "name": "Tanaka",
        "country_code": "JP",
        "language_code": "ja",
        "relationship_type": "PARTNER",
        "organization": "ABC Design",
    },
    {
        "email": "alex@example.com",
        "name": "Alex",
        "country_code": "US",
        "language_code": "en",
        "relationship_type": "CLIENT",
        "organization": "Example Inc.",
    },
]


def seed_recipients() -> None:
    with SessionLocal() as db:
        existing_emails = set(
            db.scalars(
                select(RecipientProfile.email).where(
                    RecipientProfile.email.in_(
                        [recipient["email"] for recipient in RECIPIENTS]
                    )
                )
            )
        )
        recipients = [
            RecipientProfile(**recipient)
            for recipient in RECIPIENTS
            if recipient["email"] not in existing_emails
        ]
        db.add_all(recipients)
        db.commit()
        print(f"Seeded {len(recipients)} recipient profile(s).")


if __name__ == "__main__":
    seed_recipients()
