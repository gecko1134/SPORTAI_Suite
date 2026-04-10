"""Add NIL Program and Equipment Exchange tables

Revision ID: 007_s1_nil_equipment
Revises: 006_org_structure
Create Date: 2026-04-09

Sprint 1 — Level Playing Field Foundation
Tables added:
  NIL Program: nil_athletes, nil_deals, nil_compliance_events
  Equipment Exchange: equipment_items, drop_box_locations, exchange_transactions
"""

from alembic import op
import sqlalchemy as sa

revision      = '007_s1_nil_equipment'
down_revision = '006_org_structure'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── NIL Athletes ──────────────────────────────────────────────────────────
    op.create_table('nil_athletes',
        sa.Column('id',                sa.String(36),   nullable=False),
        sa.Column('first_name',        sa.String(100),  nullable=False),
        sa.Column('last_name',         sa.String(100),  nullable=False),
        sa.Column('email',             sa.String(255),  nullable=True),
        sa.Column('phone',             sa.String(20),   nullable=True),
        sa.Column('school',            sa.String(200),  nullable=False),
        sa.Column('grade',             sa.Enum('9th','10th','11th','12th', name='gradelevel'), nullable=False),
        sa.Column('sport_primary',     sa.Enum('flag_football','soccer','lacrosse','volleyball','softball','basketball','pickleball','robotics','multi_sport','other', name='nil_sport'), nullable=False),
        sa.Column('sport_secondary',   sa.Enum('flag_football','soccer','lacrosse','volleyball','softball','basketball','pickleball','robotics','multi_sport','other', name='nil_sport_sec'), nullable=True),
        sa.Column('gpa',               sa.Float(),      nullable=True),
        sa.Column('social_followers',  sa.Integer(),    nullable=False, server_default='0'),
        sa.Column('bio',               sa.Text(),       nullable=True),
        sa.Column('is_active',         sa.Boolean(),    nullable=False, server_default='true'),
        sa.Column('enrolled_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('graduation_date',   sa.Date(),       nullable=True),
        sa.Column('compliance_status', sa.Enum('compliant','pending_review','warning','violation', name='compliancestatus'), nullable=False, server_default='compliant'),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_nil_athletes_school',    'nil_athletes', ['school'])
    op.create_index('ix_nil_athletes_sport',     'nil_athletes', ['sport_primary'])
    op.create_index('ix_nil_athletes_compliance','nil_athletes', ['compliance_status'])

    # ── NIL Deals ─────────────────────────────────────────────────────────────
    op.create_table('nil_deals',
        sa.Column('id',                      sa.String(36),  nullable=False),
        sa.Column('athlete_id',              sa.String(36),  nullable=False),
        sa.Column('brand_name',              sa.String(200), nullable=False),
        sa.Column('deal_type',               sa.Enum('social_media','appearance','equipment','camp_promotion','community_service','ambassador','content_creation','other', name='dealtype'), nullable=False),
        sa.Column('deal_value',              sa.Float(),     nullable=False, server_default='0'),
        sa.Column('status',                  sa.Enum('active','pending','completed','cancelled','expired', name='dealstatus'), nullable=False, server_default='active'),
        sa.Column('start_date',              sa.Date(),      nullable=False),
        sa.Column('end_date',                sa.Date(),      nullable=True),
        sa.Column('deliverables',            sa.Text(),      nullable=True),
        sa.Column('social_posts_required',   sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('social_posts_completed',  sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('appearances_required',    sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('appearances_completed',   sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('notes',                   sa.Text(),      nullable=True),
        sa.Column('contract_url',            sa.String(500), nullable=True),
        sa.Column('created_at',              sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',              sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['athlete_id'], ['nil_athletes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_nil_deals_athlete',  'nil_deals', ['athlete_id'])
    op.create_index('ix_nil_deals_status',   'nil_deals', ['status'])
    op.create_index('ix_nil_deals_end_date', 'nil_deals', ['end_date'])

    # ── NIL Compliance Events ─────────────────────────────────────────────────
    op.create_table('nil_compliance_events',
        sa.Column('id',            sa.String(36),  nullable=False),
        sa.Column('athlete_id',    sa.String(36),  nullable=False),
        sa.Column('event_type',    sa.String(100), nullable=False),
        sa.Column('status',        sa.Enum('compliant','pending_review','warning','violation', name='compliancestatus2'), nullable=False),
        sa.Column('notes',         sa.Text(),      nullable=True),
        sa.Column('due_date',      sa.Date(),      nullable=True),
        sa.Column('resolved_date', sa.Date(),      nullable=True),
        sa.Column('created_at',    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['athlete_id'], ['nil_athletes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Drop Box Locations ────────────────────────────────────────────────────
    op.create_table('drop_box_locations',
        sa.Column('id',                  sa.String(36),  nullable=False),
        sa.Column('name',                sa.String(200), nullable=False),
        sa.Column('address',             sa.String(500), nullable=False),
        sa.Column('city',                sa.String(100), nullable=False),
        sa.Column('state',               sa.String(10),  nullable=False, server_default='MN'),
        sa.Column('zip_code',            sa.String(10),  nullable=True),
        sa.Column('contact_name',        sa.String(200), nullable=True),
        sa.Column('contact_phone',       sa.String(20),  nullable=True),
        sa.Column('status',              sa.Enum('active','full','inactive','scheduled', name='dropboxstatus'), nullable=False, server_default='active'),
        sa.Column('capacity',            sa.Integer(),   nullable=False, server_default='50'),
        sa.Column('sports_accepted',     sa.String(500), nullable=False, server_default='all'),
        sa.Column('last_pickup_date',    sa.Date(),      nullable=True),
        sa.Column('next_pickup_date',    sa.Date(),      nullable=True),
        sa.Column('items_collected_ytd', sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('is_active',           sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_dropbox_city',   'drop_box_locations', ['city'])
    op.create_index('ix_dropbox_status', 'drop_box_locations', ['status'])

    # ── Equipment Items ───────────────────────────────────────────────────────
    op.create_table('equipment_items',
        sa.Column('id',            sa.String(36),  nullable=False),
        sa.Column('name',          sa.String(200), nullable=False),
        sa.Column('sport',         sa.Enum('flag_football','soccer','lacrosse','volleyball','softball','basketball','pickleball','robotics', name='eqsport'), nullable=False),
        sa.Column('tier',          sa.Enum('manufacturer','consignment','rental', name='equipmenttier'), nullable=False),
        sa.Column('condition',     sa.Enum('new','excellent','good','fair','poor', name='itemcondition'), nullable=False),
        sa.Column('status',        sa.Enum('available','checked_out','reserved','maintenance','retired', name='itemstatus'), nullable=False, server_default='available'),
        sa.Column('size',          sa.String(50),  nullable=True),
        sa.Column('brand',         sa.String(100), nullable=True),
        sa.Column('sku',           sa.String(100), nullable=True),
        sa.Column('retail_value',  sa.Float(),     nullable=False, server_default='0'),
        sa.Column('rental_rate',   sa.Float(),     nullable=False, server_default='0'),
        sa.Column('drop_box_id',   sa.String(36),  nullable=True),
        sa.Column('notes',         sa.Text(),      nullable=True),
        sa.Column('received_date', sa.Date(),      nullable=False),
        sa.Column('is_active',     sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['drop_box_id'], ['drop_box_locations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_equipment_sport',  'equipment_items', ['sport'])
    op.create_index('ix_equipment_tier',   'equipment_items', ['tier'])
    op.create_index('ix_equipment_status', 'equipment_items', ['status'])

    # ── Exchange Transactions ─────────────────────────────────────────────────
    op.create_table('exchange_transactions',
        sa.Column('id',                sa.String(36),  nullable=False),
        sa.Column('item_id',           sa.String(36),  nullable=False),
        sa.Column('transaction_type',  sa.Enum('donation','exchange','rental','return','consignment', name='transactiontype'), nullable=False),
        sa.Column('recipient_name',    sa.String(200), nullable=True),
        sa.Column('recipient_age',     sa.Integer(),   nullable=True),
        sa.Column('recipient_school',  sa.String(200), nullable=True),
        sa.Column('donor_name',        sa.String(200), nullable=True),
        sa.Column('drop_box_id',       sa.String(36),  nullable=True),
        sa.Column('rental_days',       sa.Integer(),   nullable=True),
        sa.Column('rental_revenue',    sa.Float(),     nullable=False, server_default='0'),
        sa.Column('transaction_date',  sa.Date(),      nullable=False),
        sa.Column('return_date',       sa.Date(),      nullable=True),
        sa.Column('notes',             sa.Text(),      nullable=True),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['item_id'],      ['equipment_items.id'],     ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['drop_box_id'],  ['drop_box_locations.id'],  ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_exchange_txn_date', 'exchange_transactions', ['transaction_date'])
    op.create_index('ix_exchange_txn_type', 'exchange_transactions', ['transaction_type'])


def downgrade() -> None:
    op.drop_table('exchange_transactions')
    op.drop_table('equipment_items')
    op.drop_table('drop_box_locations')
    op.drop_table('nil_compliance_events')
    op.drop_table('nil_deals')
    op.drop_table('nil_athletes')

    for enum_name in ['gradelevel','nil_sport','nil_sport_sec','compliancestatus','dealtype',
                      'dealstatus','compliancestatus2','dropboxstatus','eqsport',
                      'equipmenttier','itemcondition','itemstatus','transactiontype']:
        op.execute(f'DROP TYPE IF EXISTS {enum_name}')
