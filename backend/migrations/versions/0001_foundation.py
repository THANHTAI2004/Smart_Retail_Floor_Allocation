"""Initial durable project, input aggregate, order and queue schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("revision", sa.Integer, nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("sections", sa.JSON, nullable=False),
    )
    op.create_table(
        "product_keys",
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("sku", sa.String(120), primary_key=True),
    )
    op.create_table(
        "orders",
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("id", sa.String(120), primary_key=True),
        sa.Column("placed_at", sa.String(50), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("due_s", sa.Float, nullable=False),
        sa.CheckConstraint("due_s > 0"),
    )
    op.create_table(
        "order_lines",
        sa.Column("project_id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(120), primary_key=True),
        sa.Column("sku", sa.String(120), primary_key=True),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(["project_id", "order_id"], ["orders.project_id", "orders.id"]),
        sa.ForeignKeyConstraint(
            ["project_id", "sku"], ["product_keys.project_id", "product_keys.sku"]
        ),
        sa.CheckConstraint("quantity > 0"),
    )
    op.create_table(
        "optimization_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("project_revision", sa.Integer, nullable=False),
        sa.Column("input_sha256", sa.String(64), nullable=False),
        sa.Column("snapshot", sa.JSON, nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("stage", sa.String(20), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("started_epoch", sa.Float),
        sa.Column("result", sa.JSON),
        sa.Column("error", sa.JSON),
        sa.Column("result_sha256", sa.String(64)),
    )
    op.create_index("ix_optimization_runs_project_id", "optimization_runs", ["project_id"])
    op.create_index("ix_optimization_runs_status", "optimization_runs", ["status"])
    op.create_table(
        "worker_heartbeats",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("epoch", sa.Float, nullable=False),
    )


def downgrade():
    for table in (
        "worker_heartbeats",
        "optimization_runs",
        "order_lines",
        "orders",
        "product_keys",
        "projects",
    ):
        op.drop_table(table)
