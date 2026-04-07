"""Add garage_items table for creator product wishlist.

Revision ID: 20260406_0001
Revises: 20260330_0002
Create Date: 2026-04-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260406_0001"
down_revision = "20260330_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "garage_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_garage_items_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_garage_items")),
        sa.UniqueConstraint("product_id", name=op.f("uq_garage_items_product_id")),
    )


def downgrade() -> None:
    op.drop_table("garage_items")
