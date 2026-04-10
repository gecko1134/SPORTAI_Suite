"""Add Skill Shot Academy and PuttView AR tables

Revision ID: 010_s4_phase2_flagship
Revises: 009_s3_hospitality
Create Date: 2026-04-09

Sprint 4 — NGP Development Phase 2 Flagship
Skill Shot: skill_shot_bays, skill_shot_sessions, skill_shot_milestones, skill_shot_capital
PuttView AR: puttview_sessions, puttview_revenue_ledger, puttview_roi_snapshots
"""

from alembic import op
import sqlalchemy as sa

revision      = '010_s4_phase2_flagship'
down_revision = '009_s3_hospitality'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Skill Shot Bays ───────────────────────────────────────────────────────
    op.create_table('skill_shot_bays',
        sa.Column('id',                sa.String(36),  nullable=False),
        sa.Column('bay_number',        sa.Integer(),   nullable=False),
        sa.Column('status',            sa.Enum('planned','installation','calibration','operational','maintenance', name='baystatus'), nullable=False, server_default='planned'),
        sa.Column('trackman_serial',   sa.String(100), nullable=True),
        sa.Column('installation_date', sa.Date(),      nullable=True),
        sa.Column('operational_date',  sa.Date(),      nullable=True),
        sa.Column('sessions_total',    sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('revenue_total',     sa.Float(),     nullable=False, server_default='0'),
        sa.Column('notes',             sa.Text(),      nullable=True),
        sa.Column('is_active',         sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bay_number'),
    )
    op.create_index('ix_ss_bays_status', 'skill_shot_bays', ['status'])

    # ── Skill Shot Sessions ───────────────────────────────────────────────────
    op.create_table('skill_shot_sessions',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('bay_id',          sa.String(36),  nullable=False),
        sa.Column('session_type',    sa.Enum('individual','group','lesson','league','corporate','simulator', name='ssessiontype'), nullable=False),
        sa.Column('guest_name',      sa.String(200), nullable=False),
        sa.Column('guest_count',     sa.Integer(),   nullable=False, server_default='1'),
        sa.Column('session_date',    sa.Date(),      nullable=False),
        sa.Column('duration_hours',  sa.Float(),     nullable=False),
        sa.Column('rate_per_hour',   sa.Float(),     nullable=False),
        sa.Column('revenue',         sa.Float(),     nullable=False),
        sa.Column('instructor_name', sa.String(200), nullable=True),
        sa.Column('is_member',       sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('notes',           sa.Text(),      nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['bay_id'], ['skill_shot_bays.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ss_sessions_date', 'skill_shot_sessions', ['session_date'])
    op.create_index('ix_ss_sessions_type', 'skill_shot_sessions', ['session_type'])

    # ── Skill Shot Milestones ─────────────────────────────────────────────────
    op.create_table('skill_shot_milestones',
        sa.Column('id',             sa.String(36),  nullable=False),
        sa.Column('phase',          sa.Integer(),   nullable=False),
        sa.Column('title',          sa.String(300), nullable=False),
        sa.Column('description',    sa.Text(),      nullable=True),
        sa.Column('status',         sa.Enum('not_started','in_progress','completed','at_risk','blocked', name='milestonestatus'), nullable=False, server_default='not_started'),
        sa.Column('target_date',    sa.Date(),      nullable=True),
        sa.Column('completed_date', sa.Date(),      nullable=True),
        sa.Column('owner',          sa.String(200), nullable=True),
        sa.Column('progress_pct',   sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('blockers',       sa.Text(),      nullable=True),
        sa.Column('created_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ss_milestones_phase',  'skill_shot_milestones', ['phase'])
    op.create_index('ix_ss_milestones_status', 'skill_shot_milestones', ['status'])

    # ── Skill Shot Capital ────────────────────────────────────────────────────
    op.create_table('skill_shot_capital',
        sa.Column('id',               sa.String(36), nullable=False),
        sa.Column('source',           sa.Enum('sba_504','naming_rights','state_grants','crowdfunding','operating_cash','other', name='capitalsource'), nullable=False),
        sa.Column('label',            sa.String(200), nullable=False),
        sa.Column('target_amount',    sa.Float(),    nullable=False),
        sa.Column('committed_amount', sa.Float(),    nullable=False, server_default='0'),
        sa.Column('received_amount',  sa.Float(),    nullable=False, server_default='0'),
        sa.Column('deployed_amount',  sa.Float(),    nullable=False, server_default='0'),
        sa.Column('status',           sa.String(50), nullable=False, server_default='pending'),
        sa.Column('notes',            sa.Text(),     nullable=True),
        sa.Column('updated_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source'),
    )

    # ── PuttView Sessions ─────────────────────────────────────────────────────
    op.create_table('puttview_sessions',
        sa.Column('id',                sa.String(36),  nullable=False),
        sa.Column('bay_number',        sa.Integer(),   nullable=False),
        sa.Column('session_mode',      sa.Enum('open_play','lesson','league','corporate','event','tournament', name='sessionmode'), nullable=False),
        sa.Column('guest_name',        sa.String(200), nullable=False),
        sa.Column('skill_level',       sa.Enum('beginner','intermediate','advanced','professional', name='skilllevel'), nullable=True),
        sa.Column('guest_count',       sa.Integer(),   nullable=False, server_default='1'),
        sa.Column('session_date',      sa.Date(),      nullable=False),
        sa.Column('duration_minutes',  sa.Integer(),   nullable=False),
        sa.Column('rate',              sa.Float(),     nullable=False),
        sa.Column('revenue',           sa.Float(),     nullable=False),
        sa.Column('is_member',         sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('putts_attempted',   sa.Integer(),   nullable=True),
        sa.Column('putts_made',        sa.Integer(),   nullable=True),
        sa.Column('notes',             sa.Text(),      nullable=True),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_pv_sessions_date', 'puttview_sessions', ['session_date'])
    op.create_index('ix_pv_sessions_mode', 'puttview_sessions', ['session_mode'])
    op.create_index('ix_pv_sessions_bay',  'puttview_sessions', ['bay_number'])

    # ── PuttView Revenue Ledger ───────────────────────────────────────────────
    op.create_table('puttview_revenue_ledger',
        sa.Column('id',               sa.String(36), nullable=False),
        sa.Column('month',            sa.String(7),  nullable=False),
        sa.Column('sessions_count',   sa.Integer(),  nullable=False),
        sa.Column('revenue',          sa.Float(),    nullable=False),
        sa.Column('target_monthly',   sa.Float(),    nullable=False),
        sa.Column('bays_active',      sa.Integer(),  nullable=False),
        sa.Column('utilization_pct',  sa.Float(),    nullable=False),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('month'),
    )

    # ── PuttView ROI Snapshots ────────────────────────────────────────────────
    op.create_table('puttview_roi_snapshots',
        sa.Column('id',                  sa.String(36), nullable=False),
        sa.Column('snapshot_date',       sa.Date(),     nullable=False),
        sa.Column('cumulative_revenue',  sa.Float(),    nullable=False),
        sa.Column('cumulative_costs',    sa.Float(),    nullable=False),
        sa.Column('net_return',          sa.Float(),    nullable=False),
        sa.Column('roi_pct',             sa.Float(),    nullable=False),
        sa.Column('months_operational',  sa.Integer(),  nullable=False),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('puttview_roi_snapshots')
    op.drop_table('puttview_revenue_ledger')
    op.drop_table('puttview_sessions')
    op.drop_table('skill_shot_capital')
    op.drop_table('skill_shot_milestones')
    op.drop_table('skill_shot_sessions')
    op.drop_table('skill_shot_bays')
    for e in ['baystatus','ssessiontype','milestonestatus','capitalsource','sessionmode','skilllevel']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
