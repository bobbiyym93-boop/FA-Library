"""create data dictionary options

Revision ID: c3a4f5d6e7b8
Revises: 9b6f3d24a1c7
"""
from alembic import op
import sqlalchemy as sa


revision = "c3a4f5d6e7b8"
down_revision = "9b6f3d24a1c7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "data_dictionary_options",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dictionary_type", sa.String(length=30), nullable=False),
        sa.Column("value", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dictionary_type", "value", name="uq_dictionary_type_value"),
    )
    with op.batch_alter_table("data_dictionary_options") as batch_op:
        batch_op.create_index(
            batch_op.f("ix_data_dictionary_options_dictionary_type"),
            ["dictionary_type"],
            unique=False,
        )
    from datetime import datetime, timezone
    table = sa.table(
        "data_dictionary_options",
        sa.column("dictionary_type", sa.String),
        sa.column("value", sa.String),
        sa.column("sort_order", sa.Integer),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    now = datetime.now(timezone.utc)
    defaults = {
        "project": ("Project1", "Project2", "Project3"),
        "product": ("Product1", "Product2", "Product3"),
        "technology": ("Technology1", "Technology2", "Technology3"),
    }
    op.bulk_insert(table, [
        {"dictionary_type": dictionary_type, "value": value, "sort_order": index, "created_at": now, "updated_at": now}
        for dictionary_type, values in defaults.items()
        for index, value in enumerate(values)
    ])


def downgrade():
    with op.batch_alter_table("data_dictionary_options") as batch_op:
        batch_op.drop_index(batch_op.f("ix_data_dictionary_options_dictionary_type"))
    op.drop_table("data_dictionary_options")
