"""Authorized users

Revision ID: 2bbb7832872
Revises: 43cc3d10034
Create Date: 2015-12-14 00:57:44.115465

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2bbb7832872"
down_revision = "43cc3d10034"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "authorized_users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("email"),
    )


def downgrade():
    op.drop_table("authorized_users")
