"""Add Cross-Entity Command Center and SaaS Admin v11 tables

Revision ID: 015_s9_command_saas
Revises: 014_s8_membership_capital
Create Date: 2026-04-09

Sprint 9 — Final Integration Capstone
Command Center: entity_health_snapshots, executive_summaries, anomaly_alerts
SaaS Admin: saas_tenants_v11, api_keys_v11, white_label_configs_v11
"""

from alembic import op
import sqlalchemy as sa

revision      = '015_s9_command_saas'
down_revision = '014_s8_membership_capital'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Entity Health Snapshots ───────────────────────────────────────────────
    op.create_table('entity_health_snapshots',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('entity',           sa.Enum('nexus_domes','nxs_national_complex','lpf_foundation','ngp_development', name='entityenum'), nullable=False),
        sa.Column('snapshot_date',    sa.String(10),  nullable=False),
        sa.Column('health_score',     sa.Integer(),   nullable=False),
        sa.Column('revenue_score',    sa.Integer(),   nullable=False),
        sa.Column('operations_score', sa.Integer(),   nullable=False),
        sa.Column('growth_score',     sa.Integer(),   nullable=False),
        sa.Column('compliance_score', sa.Integer(),   nullable=False),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_entity_health_date',   'entity_health_snapshots', ['snapshot_date'])
    op.create_index('ix_entity_health_entity', 'entity_health_snapshots', ['entity'])

    # ── Executive Summaries ───────────────────────────────────────────────────
    op.create_table('executive_summaries',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('period',           sa.Enum('weekly','monthly','annual', name='summaryperiod'), nullable=False),
        sa.Column('period_label',     sa.String(50),  nullable=False),
        sa.Column('summary_text',     sa.Text(),      nullable=False),
        sa.Column('headline_metric',  sa.String(200), nullable=True),
        sa.Column('entity_focus',     sa.String(20),  nullable=False, server_default='all'),
        sa.Column('generated_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exec_summaries_period', 'executive_summaries', ['period'])

    # ── Anomaly Alerts ────────────────────────────────────────────────────────
    op.create_table('anomaly_alerts',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('module',          sa.String(100), nullable=False),
        sa.Column('entity',          sa.Enum('nexus_domes','nxs_national_complex','lpf_foundation','ngp_development', name='entityenum2'), nullable=False),
        sa.Column('level',           sa.Enum('info','warning','critical', name='anomalylevel'), nullable=False),
        sa.Column('title',           sa.String(300), nullable=False),
        sa.Column('description',     sa.Text(),      nullable=False),
        sa.Column('metric_name',     sa.String(100), nullable=False),
        sa.Column('metric_value',    sa.Float(),     nullable=False),
        sa.Column('expected_value',  sa.Float(),     nullable=False),
        sa.Column('deviation_pct',   sa.Float(),     nullable=False),
        sa.Column('is_resolved',     sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('identified_at',   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('resolved_at',     sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_anomaly_entity',   'anomaly_alerts', ['entity'])
    op.create_index('ix_anomaly_level',    'anomaly_alerts', ['level'])
    op.create_index('ix_anomaly_resolved', 'anomaly_alerts', ['is_resolved'])

    # ── SaaS Tenants v11 ─────────────────────────────────────────────────────
    op.create_table('saas_tenants_v11',
        sa.Column('id',                  sa.String(36),  nullable=False),
        sa.Column('name',                sa.String(200), nullable=False),
        sa.Column('contact_name',        sa.String(200), nullable=False),
        sa.Column('contact_email',       sa.String(255), nullable=False),
        sa.Column('plan',                sa.Enum('starter','professional','enterprise', name='tierplan'), nullable=False),
        sa.Column('status',              sa.Enum('trial','active','paused','churned', name='tenantstatus'), nullable=False, server_default='trial'),
        sa.Column('monthly_revenue',     sa.Float(),     nullable=False, server_default='0'),
        sa.Column('trial_end',           sa.String(10),  nullable=True),
        sa.Column('subscription_start',  sa.String(10),  nullable=True),
        sa.Column('city',                sa.String(100), nullable=True),
        sa.Column('state',               sa.String(10),  nullable=True),
        sa.Column('facility_type',       sa.String(100), nullable=True),
        sa.Column('api_calls_mtd',       sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('modules_enabled',     sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('white_label',         sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('notes',               sa.Text(),      nullable=True),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_saas_tenants_plan',   'saas_tenants_v11', ['plan'])
    op.create_index('ix_saas_tenants_status', 'saas_tenants_v11', ['status'])

    # ── API Keys v11 ──────────────────────────────────────────────────────────
    op.create_table('api_keys_v11',
        sa.Column('id',                 sa.String(36),  nullable=False),
        sa.Column('tenant_id',          sa.String(36),  nullable=False),
        sa.Column('key_prefix',         sa.String(20),  nullable=False),
        sa.Column('key_hash',           sa.String(64),  nullable=False),
        sa.Column('label',              sa.String(200), nullable=False),
        sa.Column('status',             sa.Enum('active','revoked','expired', name='keystatus'), nullable=False, server_default='active'),
        sa.Column('rate_limit_per_min', sa.Integer(),   nullable=False, server_default='60'),
        sa.Column('calls_total',        sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('last_used_at',       sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at',         sa.String(10),  nullable=True),
        sa.Column('created_at',         sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_api_keys_tenant', 'api_keys_v11', ['tenant_id'])
    op.create_index('ix_api_keys_status', 'api_keys_v11', ['status'])

    # ── White-Label Configs v11 ───────────────────────────────────────────────
    op.create_table('white_label_configs_v11',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('tenant_id',        sa.String(36),  nullable=False),
        sa.Column('platform_name',    sa.String(200), nullable=False),
        sa.Column('primary_color',    sa.String(7),   nullable=False, server_default='#C9A84C'),
        sa.Column('secondary_color',  sa.String(7),   nullable=False, server_default='#0A2240'),
        sa.Column('logo_url',         sa.String(500), nullable=True),
        sa.Column('favicon_url',      sa.String(500), nullable=True),
        sa.Column('custom_domain',    sa.String(200), nullable=True),
        sa.Column('hide_powered_by',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('updated_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id'),
    )


def downgrade() -> None:
    op.drop_table('white_label_configs_v11')
    op.drop_table('api_keys_v11')
    op.drop_table('saas_tenants_v11')
    op.drop_table('anomaly_alerts')
    op.drop_table('executive_summaries')
    op.drop_table('entity_health_snapshots')
    for e in ['entityenum','entityenum2','summaryperiod','anomalylevel','tierplan','tenantstatus','keystatus']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
