"""remove wpv.edit_summary

Revision ID: 4456da3ec475
Revises: 2ad7596b10cd
Create Date: 2020-11-22 09:33:58.838252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4456da3ec475'
down_revision = '2ad7596b10cd'
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
