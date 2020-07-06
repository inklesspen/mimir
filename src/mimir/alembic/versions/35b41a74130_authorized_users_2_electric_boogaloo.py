"""Authorized users 2: Electric Boogaloo

Revision ID: 35b41a74130
Revises: 2bbb7832872
Create Date: 2015-12-20 19:24:19.301136

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "35b41a74130"
down_revision = "2bbb7832872"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("authorized_users")
    op.create_table(
        "authorized_users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.Unicode, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.drop_column("audit_entries", "credential_id")
    op.add_column("audit_entries", sa.Column("user_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        None, "audit_entries", "authorized_users", ["user_id"], ["id"]
    )


def downgrade():
    op.drop_column("audit_entries", "user_id")
    op.add_column(
        "audit_entries", sa.Column("credential_id", sa.Integer, nullable=False)
    )
    op.create_foreign_key(
        "audit_entries_credential_id_fkey",
        "audit_entries",
        "credentials",
        ["credential_id"],
        ["id"],
    )
    op.drop_table("authorized_users")
    op.create_table(
        "authorized_users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("email"),
    )
