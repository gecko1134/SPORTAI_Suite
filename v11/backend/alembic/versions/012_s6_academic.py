"""Add Academic Programs tables

Revision ID: 012_s6_academic
Revises: 011_s5_rink_fnb
Create Date: 2026-04-09

Sprint 6 — NXS Academic Partnership Program
Tables: academic_partners, scholarship_hours, recruiting_matches,
        academic_schedule_blocks, academic_compliance_records
"""

from alembic import op
import sqlalchemy as sa

revision      = '012_s6_academic'
down_revision = '011_s5_rink_fnb'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Academic Partners ─────────────────────────────────────────────────────
    op.create_table('academic_partners',
        sa.Column('id',                        sa.String(36),  nullable=False),
        sa.Column('institution_name',          sa.String(200), nullable=False),
        sa.Column('level',                     sa.Enum('high_school','community_college','college','university','club_program', name='institutionlevel'), nullable=False),
        sa.Column('city',                      sa.String(100), nullable=False),
        sa.Column('state',                     sa.String(10),  nullable=False, server_default='MN'),
        sa.Column('primary_contact',           sa.String(200), nullable=False),
        sa.Column('contact_email',             sa.String(255), nullable=True),
        sa.Column('contact_phone',             sa.String(20),  nullable=True),
        sa.Column('status',                    sa.Enum('prospect','negotiating','active','renewal','lapsed', name='partnerstatus'), nullable=False, server_default='prospect'),
        sa.Column('sports',                    sa.String(500), nullable=False),
        sa.Column('student_athletes',          sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('annual_contract_value',     sa.Float(),     nullable=False, server_default='0'),
        sa.Column('partnership_start',         sa.Date(),      nullable=True),
        sa.Column('partnership_end',           sa.Date(),      nullable=True),
        sa.Column('scholarship_hours_granted', sa.Float(),     nullable=False, server_default='0'),
        sa.Column('scholarship_hours_used',    sa.Float(),     nullable=False, server_default='0'),
        sa.Column('notes',                     sa.Text(),      nullable=True),
        sa.Column('is_active',                 sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('created_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_acad_partners_level',  'academic_partners', ['level'])
    op.create_index('ix_acad_partners_status', 'academic_partners', ['status'])
    op.create_index('ix_acad_partners_city',   'academic_partners', ['city'])

    # ── Scholarship Hours ─────────────────────────────────────────────────────
    op.create_table('scholarship_hours',
        sa.Column('id',                sa.String(36),  nullable=False),
        sa.Column('partner_id',        sa.String(36),  nullable=False),
        sa.Column('scholarship_type',  sa.Enum('practice_hours','tournament_entry','equipment_access','coaching_clinic','game_film', name='scholarshiptype'), nullable=False),
        sa.Column('sport',             sa.Enum('flag_football','soccer','lacrosse','volleyball','softball','basketball','pickleball','robotics','ice_hockey','multi_sport', name='acadsport'), nullable=False),
        sa.Column('hours_granted',     sa.Float(),     nullable=False),
        sa.Column('hours_used',        sa.Float(),     nullable=False, server_default='0'),
        sa.Column('dollar_value',      sa.Float(),     nullable=False),
        sa.Column('grant_date',        sa.Date(),      nullable=False),
        sa.Column('expiry_date',       sa.Date(),      nullable=True),
        sa.Column('description',       sa.String(300), nullable=True),
        sa.Column('approved_by',       sa.String(200), nullable=True),
        sa.Column('created_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['partner_id'], ['academic_partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_sch_hours_partner', 'scholarship_hours', ['partner_id'])

    # ── Recruiting Matches ────────────────────────────────────────────────────
    op.create_table('recruiting_matches',
        sa.Column('id',                  sa.String(36),  nullable=False),
        sa.Column('partner_id',          sa.String(36),  nullable=False),
        sa.Column('athlete_name',        sa.String(200), nullable=False),
        sa.Column('athlete_school',      sa.String(200), nullable=False),
        sa.Column('athlete_grad_year',   sa.Integer(),   nullable=False),
        sa.Column('sport',               sa.Enum('flag_football','soccer','lacrosse','volleyball','softball','basketball','pickleball','robotics','ice_hockey','multi_sport', name='acadsport2'), nullable=False),
        sa.Column('gpa',                 sa.Float(),     nullable=True),
        sa.Column('match_score',         sa.Integer(),   nullable=False),
        sa.Column('status',              sa.Enum('pending','contacted','visited','committed','declined', name='recruitingstatus'), nullable=False, server_default='pending'),
        sa.Column('match_rationale',     sa.Text(),      nullable=True),
        sa.Column('contacted_date',      sa.Date(),      nullable=True),
        sa.Column('visit_date',          sa.Date(),      nullable=True),
        sa.Column('outcome_notes',       sa.Text(),      nullable=True),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['partner_id'], ['academic_partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recruiting_partner', 'recruiting_matches', ['partner_id'])
    op.create_index('ix_recruiting_status',  'recruiting_matches', ['status'])
    op.create_index('ix_recruiting_score',   'recruiting_matches', ['match_score'])

    # ── Academic Schedule Blocks ──────────────────────────────────────────────
    op.create_table('academic_schedule_blocks',
        sa.Column('id',             sa.String(36),  nullable=False),
        sa.Column('partner_id',     sa.String(36),  nullable=False),
        sa.Column('sport',          sa.Enum('flag_football','soccer','lacrosse','volleyball','softball','basketball','pickleball','robotics','ice_hockey','multi_sport', name='acadsport3'), nullable=False),
        sa.Column('block_date',     sa.Date(),      nullable=False),
        sa.Column('start_time',     sa.Time(),      nullable=False),
        sa.Column('end_time',       sa.Time(),      nullable=False),
        sa.Column('duration_hours', sa.Float(),     nullable=False),
        sa.Column('facility_area',  sa.String(100), nullable=False),
        sa.Column('status',         sa.Enum('confirmed','tentative','completed','cancelled', name='acadblockstatus'), nullable=False, server_default='confirmed'),
        sa.Column('is_scholarship', sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('rate_per_hour',  sa.Float(),     nullable=False, server_default='0'),
        sa.Column('revenue',        sa.Float(),     nullable=False, server_default='0'),
        sa.Column('attendees',      sa.Integer(),   nullable=True),
        sa.Column('notes',          sa.Text(),      nullable=True),
        sa.Column('created_at',     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['partner_id'], ['academic_partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_acad_blocks_date',    'academic_schedule_blocks', ['block_date'])
    op.create_index('ix_acad_blocks_partner', 'academic_schedule_blocks', ['partner_id'])
    op.create_index('ix_acad_blocks_scholar', 'academic_schedule_blocks', ['is_scholarship'])

    # ── Academic Compliance Records ───────────────────────────────────────────
    op.create_table('academic_compliance_records',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('partner_id',       sa.String(36),  nullable=False),
        sa.Column('compliance_type',  sa.Enum('mou_renewal','liability_waiver','insurance_cert','academic_standing','background_check', name='acadcompliancetype'), nullable=False),
        sa.Column('status',           sa.String(50),  nullable=False),
        sa.Column('due_date',         sa.Date(),      nullable=True),
        sa.Column('submitted_date',   sa.Date(),      nullable=True),
        sa.Column('expiry_date',      sa.Date(),      nullable=True),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['partner_id'], ['academic_partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_acad_compliance_partner', 'academic_compliance_records', ['partner_id'])
    op.create_index('ix_acad_compliance_status',  'academic_compliance_records', ['status'])


def downgrade() -> None:
    op.drop_table('academic_compliance_records')
    op.drop_table('academic_schedule_blocks')
    op.drop_table('recruiting_matches')
    op.drop_table('scholarship_hours')
    op.drop_table('academic_partners')
    for e in ['institutionlevel','partnerstatus','scholarshiptype','acadsport','acadsport2',
              'acadsport3','recruitingstatus','acadblockstatus','acadcompliancetype']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
