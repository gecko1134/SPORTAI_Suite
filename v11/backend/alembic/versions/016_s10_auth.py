"""Add sportai_users auth table

Revision ID: 016_s10_auth
Revises: 015_s9_command_saas
Create Date: 2026-04-09
"""

from alembic import op
import sqlalchemy as sa

revision      = '016_s10_auth'
down_revision = '015_s9_command_saas'
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.create_table('sportai_users',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('username',        sa.String(100), nullable=False),
        sa.Column('email',           sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role',            sa.String(20),  nullable=False, server_default='viewer'),
        sa.Column('full_name',       sa.String(200), nullable=True),
        sa.Column('is_active',       sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('last_login',      sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_username', 'sportai_users', ['username'])
    op.create_index('ix_users_role',     'sportai_users', ['role'])


def downgrade() -> None:
    op.drop_table('sportai_users')
