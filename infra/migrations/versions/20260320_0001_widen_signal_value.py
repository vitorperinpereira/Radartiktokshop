"""Widen signal_value to NUMERIC(20, 4) to handle large revenue values.

Revision ID: 20260320_0001
Revises: 20260312_0001
Create Date: 2026-03-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260320_0001"
down_revision = "20260312_0001"
branch_labels = None
depends_on = None


def _alter_signal_value_column(*, type_: sa.Numeric) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("product_signals", recreate="always") as batch_op:
            batch_op.alter_column(
                "signal_value",
                existing_type=sa.Numeric(precision=10, scale=4),
                existing_nullable=True,
                type_=type_,
            )
        return

    op.alter_column(
        "product_signals",
        "signal_value",
        type_=type_,
        existing_type=sa.Numeric(precision=10, scale=4),
        existing_nullable=True,
    )


def upgrade() -> None:
    _alter_signal_value_column(type_=sa.Numeric(precision=20, scale=4))


def downgrade() -> None:
    _alter_signal_value_column(type_=sa.Numeric(precision=10, scale=4))
