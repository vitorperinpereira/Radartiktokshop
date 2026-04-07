"""Add lifecycle_phase to product_scores for lifecycle classification.

Revision ID: 20260330_0001
Revises: 20260323_0001
Create Date: 2026-03-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260330_0001"
down_revision = "20260323_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "product_scores",
        sa.Column("lifecycle_phase", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("product_scores", "lifecycle_phase")
