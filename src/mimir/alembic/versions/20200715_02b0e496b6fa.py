"""remove wpv.edit_summary

Revision ID: 02b0e496b6fa
Revises: 2ad7596b10cd
Create Date: 2020-07-15 01:03:46.264477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02b0e496b6fa"
down_revision = "2ad7596b10cd"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("writeup_post_versions", "edit_summary")


def downgrade():
    op.add_column(
        "writeup_post_versions",
        # The original column was NOT NULL, but we can't restore the old values so easily.
        sa.Column("edit_summary", sa.Unicode(200), nullable=True),
    )
