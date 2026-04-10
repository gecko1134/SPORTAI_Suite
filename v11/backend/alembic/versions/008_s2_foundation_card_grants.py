"""Add Foundation Card CRM and Grant Tracker tables

Revision ID: 008_s2_foundation_card_grants
Revises: 007_s1_nil_equipment
Create Date: 2026-04-09

Sprint 2 — Level Playing Field Foundation
Tables added:
  Foundation Card CRM: foundation_card_members, card_redemptions, card_tiers
  Grant Tracker: grant_funders, grant_applications, grant_compliance_events
"""

from alembic import op
import sqlalchemy as sa

revision      = '008_s2_foundation_card_grants'
down_revision = '007_s1_nil_equipment'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Card Tiers ────────────────────────────────────────────────────────────
    op.create_table('card_tiers',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('tier',            sa.Enum('individual','family','corporate','charter', name='cardtier'), nullable=False),
        sa.Column('price',           sa.Float(),     nullable=False),
        sa.Column('target_members',  sa.Integer(),   nullable=False),
        sa.Column('current_members', sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('description',     sa.Text(),      nullable=True),
        sa.Column('is_active',       sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('updated_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tier'),
    )

    # ── Foundation Card Members ───────────────────────────────────────────────
    op.create_table('foundation_card_members',
        sa.Column('id',                  sa.String(36),  nullable=False),
        sa.Column('first_name',          sa.String(100), nullable=False),
        sa.Column('last_name',           sa.String(100), nullable=False),
        sa.Column('email',               sa.String(255), nullable=False),
        sa.Column('phone',               sa.String(20),  nullable=True),
        sa.Column('tier',                sa.Enum('individual','family','corporate','charter', name='cardtier2'), nullable=False),
        sa.Column('status',              sa.Enum('active','expired','cancelled','trial','pending', name='memberstatus'), nullable=False, server_default='active'),
        sa.Column('annual_fee',          sa.Float(),     nullable=False),
        sa.Column('member_since',        sa.Date(),      nullable=False),
        sa.Column('expiry_date',         sa.Date(),      nullable=False),
        sa.Column('renewal_risk',        sa.Enum('low','medium','high','critical', name='renewalrisk'), nullable=False, server_default='low'),
        sa.Column('family_size',         sa.Integer(),   nullable=False, server_default='1'),
        sa.Column('company_name',        sa.String(200), nullable=True),
        sa.Column('redemptions_ytd',     sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('visits_ytd',          sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('last_activity_date',  sa.Date(),      nullable=True),
        sa.Column('referral_source',     sa.String(200), nullable=True),
        sa.Column('referred_by_id',      sa.String(36),  nullable=True),
        sa.Column('notes',               sa.Text(),      nullable=True),
        sa.Column('is_active',           sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_fc_members_tier',         'foundation_card_members', ['tier'])
    op.create_index('ix_fc_members_status',       'foundation_card_members', ['status'])
    op.create_index('ix_fc_members_renewal_risk', 'foundation_card_members', ['renewal_risk'])
    op.create_index('ix_fc_members_expiry',       'foundation_card_members', ['expiry_date'])

    # ── Card Redemptions ──────────────────────────────────────────────────────
    op.create_table('card_redemptions',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('member_id',        sa.String(36),  nullable=False),
        sa.Column('redemption_type',  sa.Enum('equipment_discount','court_credit','camp_discount','event_access',
                                              'scholarship_referral','retail_discount','guest_pass','priority_booking',
                                              name='redemptiontype'), nullable=False),
        sa.Column('value_redeemed',   sa.Float(),     nullable=False, server_default='0'),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('redemption_date',  sa.Date(),      nullable=False),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['member_id'], ['foundation_card_members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_card_redemptions_member', 'card_redemptions', ['member_id'])
    op.create_index('ix_card_redemptions_date',   'card_redemptions', ['redemption_date'])

    # ── Grant Funders ─────────────────────────────────────────────────────────
    op.create_table('grant_funders',
        sa.Column('id',            sa.String(36),  nullable=False),
        sa.Column('funder',        sa.Enum('irrrb','mn_deed','lccmr','gmrptc','northland_foundation',
                                           'duluth_community_foundation','federal','private','other',
                                           name='funder'), nullable=False),
        sa.Column('full_name',     sa.String(300), nullable=False),
        sa.Column('focus',         sa.Text(),      nullable=True),
        sa.Column('typical_range', sa.String(100), nullable=True),
        sa.Column('contact_url',   sa.String(300), nullable=True),
        sa.Column('notes',         sa.Text(),      nullable=True),
        sa.Column('is_priority',   sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('created_at',    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('funder'),
    )

    # ── Grant Applications ────────────────────────────────────────────────────
    op.create_table('grant_applications',
        sa.Column('id',                   sa.String(36),  nullable=False),
        sa.Column('funder_id',            sa.String(36),  nullable=False),
        sa.Column('funder',               sa.Enum('irrrb','mn_deed','lccmr','gmrptc','northland_foundation',
                                                  'duluth_community_foundation','federal','private','other',
                                                  name='funder2'), nullable=False),
        sa.Column('title',                sa.String(300), nullable=False),
        sa.Column('category',             sa.Enum('capital','programming','equipment','workforce','conservation',
                                                  'tourism','technology','general_operating', name='grantcategory'), nullable=False),
        sa.Column('amount_requested',     sa.Float(),     nullable=False),
        sa.Column('amount_awarded',       sa.Float(),     nullable=True),
        sa.Column('status',               sa.Enum('drafting','submitted','under_review','awarded','declined',
                                                  'waitlisted','withdrawn', name='applicationstatus'), nullable=False, server_default='drafting'),
        sa.Column('submission_date',      sa.Date(),      nullable=True),
        sa.Column('decision_date',        sa.Date(),      nullable=True),
        sa.Column('deadline',             sa.Date(),      nullable=True),
        sa.Column('grant_period_start',   sa.Date(),      nullable=True),
        sa.Column('grant_period_end',     sa.Date(),      nullable=True),
        sa.Column('narrative',            sa.Text(),      nullable=True),
        sa.Column('lead_contact',         sa.String(200), nullable=True),
        sa.Column('notes',                sa.Text(),      nullable=True),
        sa.Column('is_active',            sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',           sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',           sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['funder_id'], ['grant_funders.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_grant_apps_funder',   'grant_applications', ['funder'])
    op.create_index('ix_grant_apps_status',   'grant_applications', ['status'])
    op.create_index('ix_grant_apps_deadline', 'grant_applications', ['deadline'])

    # ── Grant Compliance Events ───────────────────────────────────────────────
    op.create_table('grant_compliance_events',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('application_id',   sa.String(36),  nullable=False),
        sa.Column('event_type',       sa.String(100), nullable=False),
        sa.Column('status',           sa.Enum('current','due_soon','overdue','submitted','approved',
                                              name='grantcompliancestatus'), nullable=False),
        sa.Column('due_date',         sa.Date(),      nullable=True),
        sa.Column('submitted_date',   sa.Date(),      nullable=True),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['application_id'], ['grant_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_grant_compliance_app',    'grant_compliance_events', ['application_id'])
    op.create_index('ix_grant_compliance_status', 'grant_compliance_events', ['status'])


def downgrade() -> None:
    op.drop_table('grant_compliance_events')
    op.drop_table('grant_applications')
    op.drop_table('grant_funders')
    op.drop_table('card_redemptions')
    op.drop_table('foundation_card_members')
    op.drop_table('card_tiers')

    for enum_name in ['cardtier','cardtier2','memberstatus','renewalrisk','redemptiontype',
                      'funder','funder2','grantcategory','applicationstatus','grantcompliancestatus']:
        op.execute(f'DROP TYPE IF EXISTS {enum_name}')
