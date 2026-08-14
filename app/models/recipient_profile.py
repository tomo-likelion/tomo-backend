from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.email_analysis import EmailAnalysis


class RecipientProfile(Base):
    __tablename__ = "recipient_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    country_code: Mapped[str] = mapped_column(String(2))
    language_code: Mapped[str] = mapped_column(String(5))
    relationship_type: Mapped[str] = mapped_column("relationship", String(30))
    organization: Mapped[str] = mapped_column(String(255))

    email_analyses: Mapped[list["EmailAnalysis"]] = relationship(
        back_populates="recipient"
    )
