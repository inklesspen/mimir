"""Add AuditEntry

Revision ID: 4dbff7d28fd
Revises: 507e38fcd17
Create Date: 2015-07-25 23:28:01.866553

"""

from alembic import op
import sqlalchemy as sa
from mimir import models

# revision identifiers, used by Alembic.
revision = '4dbff7d28fd'
down_revision = '507e38fcd17'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Unicode(), nullable=False),
        sa.Column('timestamp', models.AwareDateTime(), nullable=False),
        sa.ForeignKeyConstraint(['credential_id'], ['credentials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('audit_entries')
