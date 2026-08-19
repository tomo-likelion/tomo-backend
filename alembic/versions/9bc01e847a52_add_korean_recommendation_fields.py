"""add Korean recommendation fields

Revision ID: 9bc01e847a52
Revises: 44ff9bd74287
Create Date: 2026-08-19 13:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9bc01e847a52"
down_revision: Union[str, Sequence[str], None] = "44ff9bd74287"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "email_analyses",
        sa.Column("korean_rewritten_subject", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "email_analyses",
        sa.Column("korean_rewritten_body", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("email_analyses", "korean_rewritten_body")
    op.drop_column("email_analyses", "korean_rewritten_subject")
