"""Add creator_products pivot table for creator-to-product tracking.

Revision ID: 20260330_0002
Revises: 20260330_0001
Create Date: 2026-03-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260330_0002"
down_revision = "20260330_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creator_products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("creator_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["creators.id"],
            name=op.f("fk_creator_products_creator_id_creators"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_creator_products_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_creator_products")),
        sa.UniqueConstraint(
            "creator_id", "product_id", name=op.f("uq_creator_products_creator_product")
        ),
    )


def downgrade() -> None:
    op.drop_table("creator_products")
