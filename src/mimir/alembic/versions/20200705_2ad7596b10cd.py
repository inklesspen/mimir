"""define writeup title collation

Revision ID: 2ad7596b10cd
Revises: 41d36feab50
Create Date: 2020-07-05 21:02:11.130409

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2ad7596b10cd"
down_revision = "41d36feab50"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE COLLATION writeuptitle (provider = icu, locale = 'en-u-ka-shifted-kr-digit-latn-space-punct-symbol', deterministic = false)"
    )


def downgrade():
    op.execute("DROP COLLATION writeuptitle")
