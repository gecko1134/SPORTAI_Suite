"""Add Hotel Revenue and Apartment/Campground tables

Revision ID: 009_s3_hospitality
Revises: 008_s2_foundation_card_grants
Create Date: 2026-04-09

Sprint 3 — NXS National Complex Hospitality
Hotel: hotel_rooms, hotel_reservations, hotel_rate_cards, hotel_tid_ledger
Lodging: apartment_units, apartment_leases, campground_sites, campground_reservations
"""

from alembic import op
import sqlalchemy as sa

revision      = '009_s3_hospitality'
down_revision = '008_s2_foundation_card_grants'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Hotel Rooms ───────────────────────────────────────────────────────────
    op.create_table('hotel_rooms',
        sa.Column('id',           sa.String(36),  nullable=False),
        sa.Column('room_number',  sa.String(10),  nullable=False),
        sa.Column('room_type',    sa.Enum('standard_king','standard_double','suite_king','accessible','tournament_block', name='roomtype'), nullable=False),
        sa.Column('floor',        sa.Integer(),   nullable=False),
        sa.Column('status',       sa.Enum('available','occupied','maintenance','blocked', name='roomstatus'), nullable=False, server_default='available'),
        sa.Column('base_rate',    sa.Float(),     nullable=False),
        sa.Column('max_occupancy',sa.Integer(),   nullable=False, server_default='2'),
        sa.Column('amenities',    sa.String(500), nullable=True),
        sa.Column('notes',        sa.Text(),      nullable=True),
        sa.Column('is_active',    sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_number'),
    )
    op.create_index('ix_hotel_rooms_type',   'hotel_rooms', ['room_type'])
    op.create_index('ix_hotel_rooms_status', 'hotel_rooms', ['status'])

    # ── Hotel Reservations ────────────────────────────────────────────────────
    op.create_table('hotel_reservations',
        sa.Column('id',             sa.String(36),  nullable=False),
        sa.Column('room_id',        sa.String(36),  nullable=False),
        sa.Column('guest_name',     sa.String(200), nullable=False),
        sa.Column('guest_email',    sa.String(255), nullable=True),
        sa.Column('guest_phone',    sa.String(20),  nullable=True),
        sa.Column('check_in',       sa.Date(),      nullable=False),
        sa.Column('check_out',      sa.Date(),      nullable=False),
        sa.Column('nights',         sa.Integer(),   nullable=False),
        sa.Column('guests',         sa.Integer(),   nullable=False, server_default='1'),
        sa.Column('rate_per_night', sa.Float(),     nullable=False),
        sa.Column('total_revenue',  sa.Float(),     nullable=False),
        sa.Column('rate_strategy',  sa.Enum('standard','tournament','peak','rescue','group', name='ratestrategy'), nullable=False, server_default='standard'),
        sa.Column('status',         sa.Enum('confirmed','checked_in','checked_out','cancelled','no_show', name='bookingstatus'), nullable=False, server_default='confirmed'),
        sa.Column('tournament_id',  sa.String(36),  nullable=True),
        sa.Column('group_name',     sa.String(200), nullable=True),
        sa.Column('source',         sa.String(100), nullable=True),
        sa.Column('notes',          sa.Text(),      nullable=True),
        sa.Column('created_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['room_id'], ['hotel_rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_hotel_res_checkin',  'hotel_reservations', ['check_in'])
    op.create_index('ix_hotel_res_status',   'hotel_reservations', ['status'])
    op.create_index('ix_hotel_res_strategy', 'hotel_reservations', ['rate_strategy'])

    # ── Hotel Rate Cards ──────────────────────────────────────────────────────
    op.create_table('hotel_rate_cards',
        sa.Column('id',         sa.String(36),  nullable=False),
        sa.Column('name',       sa.String(200), nullable=False),
        sa.Column('start_date', sa.Date(),      nullable=False),
        sa.Column('end_date',   sa.Date(),      nullable=False),
        sa.Column('strategy',   sa.Enum('standard','tournament','peak','rescue','group', name='ratestrategy2'), nullable=False),
        sa.Column('multiplier', sa.Float(),     nullable=False),
        sa.Column('reason',     sa.String(300), nullable=True),
        sa.Column('is_active',  sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Hotel TID Ledger ──────────────────────────────────────────────────────
    op.create_table('hotel_tid_ledger',
        sa.Column('id',             sa.String(36), nullable=False),
        sa.Column('month',          sa.String(7),  nullable=False),
        sa.Column('room_revenue',   sa.Float(),    nullable=False),
        sa.Column('tid_assessment', sa.Float(),    nullable=False),
        sa.Column('rooms_sold',     sa.Integer(),  nullable=False),
        sa.Column('adr',            sa.Float(),    nullable=False),
        sa.Column('occupancy_pct',  sa.Float(),    nullable=False),
        sa.Column('revpar',         sa.Float(),    nullable=False),
        sa.Column('created_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_hotel_tid_month', 'hotel_tid_ledger', ['month'])

    # ── Apartment Units ───────────────────────────────────────────────────────
    op.create_table('apartment_units',
        sa.Column('id',           sa.String(36),  nullable=False),
        sa.Column('unit_number',  sa.String(10),  nullable=False),
        sa.Column('unit_type',    sa.Enum('studio','one_bedroom','two_bedroom','three_bedroom', name='unittype'), nullable=False),
        sa.Column('floor',        sa.Integer(),   nullable=False),
        sa.Column('sqft',         sa.Integer(),   nullable=False),
        sa.Column('bedrooms',     sa.Integer(),   nullable=False),
        sa.Column('bathrooms',    sa.Float(),     nullable=False),
        sa.Column('monthly_rent', sa.Float(),     nullable=False),
        sa.Column('status',       sa.Enum('active','expiring','expired','vacant','maintenance', name='leasestatus'), nullable=False, server_default='vacant'),
        sa.Column('amenities',    sa.String(500), nullable=True),
        sa.Column('notes',        sa.Text(),      nullable=True),
        sa.Column('is_active',    sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('unit_number'),
    )
    op.create_index('ix_apt_units_type',   'apartment_units', ['unit_type'])
    op.create_index('ix_apt_units_status', 'apartment_units', ['status'])

    # ── Apartment Leases ──────────────────────────────────────────────────────
    op.create_table('apartment_leases',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('unit_id',          sa.String(36),  nullable=False),
        sa.Column('tenant_name',      sa.String(200), nullable=False),
        sa.Column('tenant_email',     sa.String(255), nullable=True),
        sa.Column('tenant_phone',     sa.String(20),  nullable=True),
        sa.Column('lease_start',      sa.Date(),      nullable=False),
        sa.Column('lease_end',        sa.Date(),      nullable=False),
        sa.Column('monthly_rent',     sa.Float(),     nullable=False),
        sa.Column('deposit',          sa.Float(),     nullable=False),
        sa.Column('is_current',       sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('renewal_offered',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['unit_id'], ['apartment_units.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_apt_leases_unit',    'apartment_leases', ['unit_id'])
    op.create_index('ix_apt_leases_current', 'apartment_leases', ['is_current'])
    op.create_index('ix_apt_leases_end',     'apartment_leases', ['lease_end'])

    # ── Campground Sites ──────────────────────────────────────────────────────
    op.create_table('campground_sites',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('site_number',     sa.String(10),  nullable=False),
        sa.Column('site_type',       sa.Enum('tent','rv_hookup','cabin','group', name='campsitetype'), nullable=False),
        sa.Column('max_guests',      sa.Integer(),   nullable=False),
        sa.Column('has_electric',    sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('has_water',       sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('has_sewer',       sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('is_pet_friendly', sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('amenities',       sa.String(500), nullable=True),
        sa.Column('notes',           sa.Text(),      nullable=True),
        sa.Column('is_active',       sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('site_number'),
    )

    # ── Campground Reservations ───────────────────────────────────────────────
    op.create_table('campground_reservations',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('site_id',         sa.String(36),  nullable=False),
        sa.Column('guest_name',      sa.String(200), nullable=False),
        sa.Column('guest_email',     sa.String(255), nullable=True),
        sa.Column('check_in',        sa.Date(),      nullable=False),
        sa.Column('check_out',       sa.Date(),      nullable=False),
        sa.Column('nights',          sa.Integer(),   nullable=False),
        sa.Column('guests',          sa.Integer(),   nullable=False, server_default='1'),
        sa.Column('rate_per_night',  sa.Float(),     nullable=False),
        sa.Column('total_revenue',   sa.Float(),     nullable=False),
        sa.Column('season',          sa.Enum('summer','fall','winter','spring', name='campseason'), nullable=False),
        sa.Column('trail_interest',  sa.String(200), nullable=True),
        sa.Column('is_team_group',   sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('status',          sa.String(20),  nullable=False, server_default='confirmed'),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['site_id'], ['campground_sites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_camp_res_checkin',  'campground_reservations', ['check_in'])
    op.create_index('ix_camp_res_season',   'campground_reservations', ['season'])
    op.create_index('ix_camp_res_team',     'campground_reservations', ['is_team_group'])


def downgrade() -> None:
    op.drop_table('campground_reservations')
    op.drop_table('campground_sites')
    op.drop_table('apartment_leases')
    op.drop_table('apartment_units')
    op.drop_table('hotel_tid_ledger')
    op.drop_table('hotel_rate_cards')
    op.drop_table('hotel_reservations')
    op.drop_table('hotel_rooms')

    for e in ['roomtype','roomstatus','ratestrategy','bookingstatus','ratestrategy2',
              'unittype','leasestatus','campsitetype','campseason']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
