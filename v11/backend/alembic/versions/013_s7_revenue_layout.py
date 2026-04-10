"""Add Revenue Maximizer and Facility Layout Optimizer tables

Revision ID: 013_s7_revenue_layout
Revises: 012_s6_academic
Create Date: 2026-04-09

Sprint 7 — AI Optimization Layer
Revenue Maximizer: revenue_opportunities, revenue_actions_log
Facility Layout: facility_zones, layout_scenarios, space_utilization_snapshots
"""

from alembic import op
import sqlalchemy as sa

revision      = '013_s7_revenue_layout'
down_revision = '012_s6_academic'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Revenue Opportunities ─────────────────────────────────────────────────
    op.create_table('revenue_opportunities',
        sa.Column('id',                        sa.String(36),  nullable=False),
        sa.Column('opportunity_type',          sa.Enum('idle_capacity','pricing_gap','cross_sell','retention_risk',
                                                       'underutilized_asset','revenue_leak','upsell','new_program',
                                                       name='opportunitytype'), nullable=False),
        sa.Column('priority',                  sa.Enum('critical','high','medium','low', name='opportunitypriority'), nullable=False),
        sa.Column('status',                    sa.Enum('open','in_progress','resolved','dismissed', name='opportunitystatus'), nullable=False, server_default='open'),
        sa.Column('module',                    sa.String(100), nullable=False),
        sa.Column('title',                     sa.String(300), nullable=False),
        sa.Column('description',               sa.Text(),      nullable=False),
        sa.Column('estimated_annual_impact',   sa.Float(),     nullable=False),
        sa.Column('effort_level',              sa.String(20),  nullable=False, server_default='medium'),
        sa.Column('recommended_action',        sa.Text(),      nullable=False),
        sa.Column('identified_at',             sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('resolved_at',               sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes',                     sa.Text(),      nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rev_opps_priority', 'revenue_opportunities', ['priority'])
    op.create_index('ix_rev_opps_status',   'revenue_opportunities', ['status'])
    op.create_index('ix_rev_opps_module',   'revenue_opportunities', ['module'])

    # ── Revenue Actions Log ───────────────────────────────────────────────────
    op.create_table('revenue_actions_log',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('opportunity_id',   sa.String(36),  nullable=False),
        sa.Column('action_taken',     sa.Text(),      nullable=False),
        sa.Column('revenue_impact',   sa.Float(),     nullable=True),
        sa.Column('logged_by',        sa.String(200), nullable=True),
        sa.Column('logged_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rev_actions_opp', 'revenue_actions_log', ['opportunity_id'])

    # ── Facility Zones ────────────────────────────────────────────────────────
    op.create_table('facility_zones',
        sa.Column('id',                        sa.String(36),  nullable=False),
        sa.Column('zone_id',                   sa.String(20),  nullable=False),
        sa.Column('name',                      sa.String(200), nullable=False),
        sa.Column('area',                      sa.String(50),  nullable=False),
        sa.Column('sqft',                      sa.Integer(),   nullable=False),
        sa.Column('primary_use',               sa.String(100), nullable=False),
        sa.Column('hourly_rate',               sa.Float(),     nullable=False),
        sa.Column('capacity',                  sa.Integer(),   nullable=False),
        sa.Column('utilization_pct',           sa.Float(),     nullable=False, server_default='0'),
        sa.Column('revenue_per_sqft_annual',   sa.Float(),     nullable=False, server_default='0'),
        sa.Column('peak_hours',                sa.String(200), nullable=True),
        sa.Column('notes',                     sa.Text(),      nullable=True),
        sa.Column('is_active',                 sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('zone_id'),
    )
    op.create_index('ix_facility_zones_area',  'facility_zones', ['area'])
    op.create_index('ix_facility_zones_util',  'facility_zones', ['utilization_pct'])

    # ── Layout Scenarios ──────────────────────────────────────────────────────
    op.create_table('layout_scenarios',
        sa.Column('id',                        sa.String(36),  nullable=False),
        sa.Column('name',                      sa.String(200), nullable=False),
        sa.Column('description',               sa.Text(),      nullable=False),
        sa.Column('zone_changes',              sa.Text(),      nullable=False),
        sa.Column('projected_revenue_change',  sa.Float(),     nullable=False),
        sa.Column('revenue_change_pct',        sa.Float(),     nullable=False),
        sa.Column('implementation_cost',       sa.Float(),     nullable=False, server_default='0'),
        sa.Column('payback_months',            sa.Integer(),   nullable=True),
        sa.Column('pros',                      sa.Text(),      nullable=False),
        sa.Column('cons',                      sa.Text(),      nullable=False),
        sa.Column('status',                    sa.String(20),  nullable=False, server_default='draft'),
        sa.Column('created_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Space Utilization Snapshots ───────────────────────────────────────────
    op.create_table('space_utilization_snapshots',
        sa.Column('id',              sa.String(36), nullable=False),
        sa.Column('zone_id',         sa.String(20), nullable=False),
        sa.Column('week_of',         sa.DateTime(), nullable=False),
        sa.Column('utilization_pct', sa.Float(),    nullable=False),
        sa.Column('hours_booked',    sa.Float(),    nullable=False),
        sa.Column('revenue',         sa.Float(),    nullable=False),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_space_snapshots_zone', 'space_utilization_snapshots', ['zone_id'])
    op.create_index('ix_space_snapshots_week', 'space_utilization_snapshots', ['week_of'])


def downgrade() -> None:
    op.drop_table('space_utilization_snapshots')
    op.drop_table('layout_scenarios')
    op.drop_table('facility_zones')
    op.drop_table('revenue_actions_log')
    op.drop_table('revenue_opportunities')
    for e in ['opportunitytype','opportunitypriority','opportunitystatus']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
