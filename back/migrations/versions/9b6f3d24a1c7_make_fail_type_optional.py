"""make fail_type optional

Revision ID: 9b6f3d24a1c7
Revises: 084d0727ee15
"""
from alembic import op
import sqlalchemy as sa

revision = "9b6f3d24a1c7"
down_revision = "084d0727ee15"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("fa_cases", "fail_type", existing_type=sa.String(length=100), nullable=True)


def downgrade():
    op.execute("UPDATE fa_cases SET fail_type = '' WHERE fail_type IS NULL")
    op.alter_column("fa_cases", "fail_type", existing_type=sa.String(length=100), nullable=False)
