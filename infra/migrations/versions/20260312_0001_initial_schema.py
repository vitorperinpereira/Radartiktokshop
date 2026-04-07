"""Initial persistence schema.

Revision ID: 20260312_0001
Revises:
Create Date: 2026-03-12 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260312_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("canonical_key", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("subcategory", sa.String(length=255), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
    )
    op.create_index("ix_products_canonical_key", "products", ["canonical_key"], unique=True)

    op.create_table(
        "creators",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("handle", sa.String(length=255), nullable=False),
        sa.Column("tier", sa.String(length=64), nullable=True),
        sa.Column("primary_niche", sa.String(length=128), nullable=True),
        sa.Column("region", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_creators")),
        sa.UniqueConstraint("handle", name=op.f("uq_creators_handle")),
    )

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("input_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("records_received", sa.Integer(), nullable=False),
        sa.Column("records_written", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_jobs")),
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("input_job_ids", sa.JSON(), nullable=False),
        sa.Column("config_version", sa.String(length=64), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pipeline_runs")),
    )

    op.create_table(
        "product_aliases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("alias_type", sa.String(length=64), nullable=False),
        sa.Column("alias_value", sa.String(length=500), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_aliases_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_aliases")),
    )

    op.create_table(
        "product_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("source_record_id", sa.String(length=255), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("orders_estimate", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("commission_rate", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_snapshots_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_snapshots")),
    )
    op.create_index(
        "ix_product_snapshots_product_id_captured_at",
        "product_snapshots",
        ["product_id", "captured_at"],
        unique=False,
    )

    op.create_table(
        "product_signals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("signal_name", sa.String(length=128), nullable=False),
        sa.Column("signal_value", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("signal_type", sa.String(length=64), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("source_kind", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_signals_product_id_products"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_signals")),
    )
    op.create_index(
        "ix_product_signals_product_id_signal_name_observed_at",
        "product_signals",
        ["product_id", "signal_name", "observed_at"],
        unique=False,
    )

    op.create_table(
        "product_scores",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("trend_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("viral_potential_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("creator_accessibility_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("saturation_penalty", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("revenue_estimate", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("final_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("classification", sa.String(length=64), nullable=True),
        sa.Column("explainability_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_product_scores_product_id_products"),
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["pipeline_runs.id"],
            name=op.f("fk_product_scores_run_id_pipeline_runs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_scores")),
    )
    op.create_index(
        "ix_product_scores_week_start_final_score",
        "product_scores",
        ["week_start", "final_score"],
        unique=False,
    )

    op.create_table(
        "content_angles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("angle_type", sa.String(length=64), nullable=False),
        sa.Column("hook_text", sa.Text(), nullable=False),
        sa.Column("supporting_rationale", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_content_angles_product_id_products"),
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["pipeline_runs.id"],
            name=op.f("fk_content_angles_run_id_pipeline_runs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_content_angles")),
    )

    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("report_payload", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["pipeline_runs.id"],
            name=op.f("fk_reports_run_id_pipeline_runs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    op.create_index("ix_reports_week_start", "reports", ["week_start"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reports_week_start", table_name="reports")
    op.drop_table("reports")
    op.drop_table("content_angles")
    op.drop_index("ix_product_scores_week_start_final_score", table_name="product_scores")
    op.drop_table("product_scores")
    op.drop_index(
        "ix_product_signals_product_id_signal_name_observed_at",
        table_name="product_signals",
    )
    op.drop_table("product_signals")
    op.drop_index(
        "ix_product_snapshots_product_id_captured_at",
        table_name="product_snapshots",
    )
    op.drop_table("product_snapshots")
    op.drop_table("product_aliases")
    op.drop_table("pipeline_runs")
    op.drop_table("ingestion_jobs")
    op.drop_table("creators")
    op.drop_index("ix_products_canonical_key", table_name="products")
    op.drop_table("products")
