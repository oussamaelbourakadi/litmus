"""run progress and cancellation columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-21

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "eval_runs",
        sa.Column("total_cases", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "eval_runs",
        sa.Column("completed_cases", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "eval_runs",
        sa.Column(
            "cancel_requested", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("eval_runs", "cancel_requested")
    op.drop_column("eval_runs", "completed_cases")
    op.drop_column("eval_runs", "total_cases")
