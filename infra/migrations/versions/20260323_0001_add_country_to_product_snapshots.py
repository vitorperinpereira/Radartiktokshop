"""Add country column to product_snapshots for Brazil-only ingestion gate.

Revision ID: 20260323_0001
Revises: 20260320_0001
Create Date: 2026-03-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260323_0001"
down_revision = "20260320_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "product_snapshots",
        sa.Column("country", sa.String(8), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("product_snapshots", "country")
