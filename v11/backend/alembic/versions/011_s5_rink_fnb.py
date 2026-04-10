"""Add Ice Rink and F&B Restaurant tables

Revision ID: 011_s5_rink_fnb
Revises: 010_s4_phase2_flagship
Create Date: 2026-04-09

Sprint 5 — NXS National Complex Operations
Ice Rink: rink_sessions, rink_league_blocks, rink_conversion_log
F&B: fnb_venues, fnb_events, fnb_food_truck_schedule, fnb_revenue_ledger
"""

from alembic import op
import sqlalchemy as sa

revision      = '011_s5_rink_fnb'
down_revision = '010_s4_phase2_flagship'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Rink Sessions ─────────────────────────────────────────────────────────
    op.create_table('rink_sessions',
        sa.Column('id',             sa.String(36),  nullable=False),
        sa.Column('surface',        sa.Enum('ice','turf', name='surfacetype'), nullable=False),
        sa.Column('category',       sa.Enum('hockey_prime','hockey_off','figure_skating','open_skate','learn_to_skate','league_block','tournament','turf_prime','turf_off','maintenance','dark', name='sessioncategory'), nullable=False),
        sa.Column('title',          sa.String(200), nullable=False),
        sa.Column('session_date',   sa.Date(),      nullable=False),
        sa.Column('start_time',     sa.Time(),      nullable=False),
        sa.Column('end_time',       sa.Time(),      nullable=False),
        sa.Column('duration_hours', sa.Float(),     nullable=False),
        sa.Column('rate_per_hour',  sa.Float(),     nullable=False),
        sa.Column('attendees',      sa.Integer(),   nullable=True),
        sa.Column('revenue',        sa.Float(),     nullable=False),
        sa.Column('status',         sa.Enum('confirmed','tentative','completed','cancelled', name='rinkbookingstatus'), nullable=False, server_default='confirmed'),
        sa.Column('group_name',     sa.String(200), nullable=True),
        sa.Column('contact_name',   sa.String(200), nullable=True),
        sa.Column('notes',          sa.Text(),      nullable=True),
        sa.Column('created_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rink_sessions_date',     'rink_sessions', ['session_date'])
    op.create_index('ix_rink_sessions_surface',  'rink_sessions', ['surface'])
    op.create_index('ix_rink_sessions_category', 'rink_sessions', ['category'])

    # ── Rink League Blocks ────────────────────────────────────────────────────
    op.create_table('rink_league_blocks',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('league_name',      sa.String(200), nullable=False),
        sa.Column('sport',            sa.String(100), nullable=False),
        sa.Column('surface',          sa.Enum('ice','turf', name='surfacetype2'), nullable=False),
        sa.Column('day_of_week',      sa.Integer(),   nullable=False),
        sa.Column('start_time',       sa.Time(),      nullable=False),
        sa.Column('end_time',         sa.Time(),      nullable=False),
        sa.Column('duration_hours',   sa.Float(),     nullable=False),
        sa.Column('teams',            sa.Integer(),   nullable=False),
        sa.Column('players_per_team', sa.Integer(),   nullable=False, server_default='15'),
        sa.Column('weekly_rate',      sa.Float(),     nullable=False),
        sa.Column('season_start',     sa.Date(),      nullable=False),
        sa.Column('season_end',       sa.Date(),      nullable=False),
        sa.Column('is_active',        sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('contact_name',     sa.String(200), nullable=True),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Rink Conversion Log ───────────────────────────────────────────────────
    op.create_table('rink_conversion_log',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('direction',        sa.Enum('turf_to_ice','ice_to_turf', name='conversiondirection'), nullable=False),
        sa.Column('conversion_date',  sa.Date(),      nullable=False),
        sa.Column('reason',           sa.String(300), nullable=True),
        sa.Column('cost',             sa.Float(),     nullable=False),
        sa.Column('duration_hours',   sa.Float(),     nullable=False),
        sa.Column('completed',        sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── FnB Venues ────────────────────────────────────────────────────────────
    op.create_table('fnb_venues',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('name',            sa.String(200), nullable=False),
        sa.Column('venue_type',      sa.Enum('main_restaurant','concession_stand','food_truck_plaza','catering_kitchen','bar_lounge', name='venuetype'), nullable=False),
        sa.Column('capacity',        sa.Integer(),   nullable=False),
        sa.Column('is_operational',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('phase_open',      sa.Integer(),   nullable=False, server_default='2'),
        sa.Column('buildout_cost',   sa.Float(),     nullable=True),
        sa.Column('description',     sa.Text(),      nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── FnB Events ────────────────────────────────────────────────────────────
    op.create_table('fnb_events',
        sa.Column('id',                   sa.String(36),  nullable=False),
        sa.Column('venue_id',             sa.String(36),  nullable=False),
        sa.Column('event_type',           sa.Enum('tournament','league_night','open_event','corporate','private_event','camp_day','open_play', name='fnbeventtype'), nullable=False),
        sa.Column('title',                sa.String(200), nullable=False),
        sa.Column('event_date',           sa.Date(),      nullable=False),
        sa.Column('attendees',            sa.Integer(),   nullable=False),
        sa.Column('per_cap_spend',        sa.Float(),     nullable=False),
        sa.Column('gross_revenue',        sa.Float(),     nullable=False),
        sa.Column('cogs_pct',             sa.Float(),     nullable=False, server_default='0.32'),
        sa.Column('net_revenue',          sa.Float(),     nullable=False),
        sa.Column('food_truck_revenue',   sa.Float(),     nullable=False, server_default='0'),
        sa.Column('catering_revenue',     sa.Float(),     nullable=False, server_default='0'),
        sa.Column('sponsor_contribution', sa.Float(),     nullable=False, server_default='0'),
        sa.Column('notes',                sa.Text(),      nullable=True),
        sa.Column('created_at',           sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['venue_id'], ['fnb_venues.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_fnb_events_date', 'fnb_events', ['event_date'])
    op.create_index('ix_fnb_events_type', 'fnb_events', ['event_type'])

    # ── FnB Food Truck Schedule ───────────────────────────────────────────────
    op.create_table('fnb_food_truck_schedule',
        sa.Column('id',                sa.String(36),  nullable=False),
        sa.Column('truck_name',        sa.String(200), nullable=False),
        sa.Column('operator_name',     sa.String(200), nullable=False),
        sa.Column('cuisine_type',      sa.String(100), nullable=False),
        sa.Column('event_date',        sa.Date(),      nullable=False),
        sa.Column('status',            sa.Enum('scheduled','active','completed','cancelled', name='foodtruckstatus'), nullable=False, server_default='scheduled'),
        sa.Column('spot_number',       sa.Integer(),   nullable=False),
        sa.Column('estimated_revenue', sa.Float(),     nullable=False, server_default='0'),
        sa.Column('actual_revenue',    sa.Float(),     nullable=True),
        sa.Column('plaza_fee',         sa.Float(),     nullable=False, server_default='150'),
        sa.Column('linked_event_id',   sa.String(36),  nullable=True),
        sa.Column('notes',             sa.Text(),      nullable=True),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_food_truck_date', 'fnb_food_truck_schedule', ['event_date'])

    # ── FnB Revenue Ledger ────────────────────────────────────────────────────
    op.create_table('fnb_revenue_ledger',
        sa.Column('id',                  sa.String(36), nullable=False),
        sa.Column('month',               sa.String(7),  nullable=False),
        sa.Column('restaurant_revenue',  sa.Float(),    nullable=False, server_default='0'),
        sa.Column('concession_revenue',  sa.Float(),    nullable=False, server_default='0'),
        sa.Column('food_truck_fees',     sa.Float(),    nullable=False, server_default='0'),
        sa.Column('catering_revenue',    sa.Float(),    nullable=False, server_default='0'),
        sa.Column('total_revenue',       sa.Float(),    nullable=False),
        sa.Column('total_events',        sa.Integer(),  nullable=False, server_default='0'),
        sa.Column('total_attendees',     sa.Integer(),  nullable=False, server_default='0'),
        sa.Column('avg_per_cap',         sa.Float(),    nullable=False, server_default='0'),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('month'),
    )


def downgrade() -> None:
    op.drop_table('fnb_revenue_ledger')
    op.drop_table('fnb_food_truck_schedule')
    op.drop_table('fnb_events')
    op.drop_table('fnb_venues')
    op.drop_table('rink_conversion_log')
    op.drop_table('rink_league_blocks')
    op.drop_table('rink_sessions')
    for e in ['surfacetype','sessioncategory','rinkbookingstatus','surfacetype2',
              'conversiondirection','venuetype','fnbeventtype','foodtruckstatus']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
