from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.recipient_profile import RecipientProfile


class EmailAnalysis(Base):
    __tablename__ = "email_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("recipient_profiles.id", ondelete="RESTRICT"),
        index=True,
    )
    original_subject: Mapped[str] = mapped_column(String(255))
    original_body: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(50))
    request_summary: Mapped[str] = mapped_column(Text)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_result: Mapped[dict[str, Any]] = mapped_column(JSON)
    rewritten_subject: Mapped[str] = mapped_column(String(255))
    rewritten_body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    recipient: Mapped["RecipientProfile"] = relationship(
        back_populates="email_analyses"
    )
