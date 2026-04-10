"""Add Membership Value Predictor and Capital Stack Tracker tables

Revision ID: 014_s8_membership_capital
Revises: 013_s7_revenue_layout
Create Date: 2026-04-09

Sprint 8 — AI Prediction + Capital Intelligence
Membership: membership_ltv_scores, churn_predictions, winback_sequences, membership_cohorts
Capital: capital_sources, capital_disbursements, investor_reports, tid_ledger
"""

from alembic import op
import sqlalchemy as sa

revision      = '014_s8_membership_capital'
down_revision = '013_s7_revenue_layout'
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── Membership LTV Scores ─────────────────────────────────────────────────
    op.create_table('membership_ltv_scores',
        sa.Column('id',                        sa.String(36),  nullable=False),
        sa.Column('member_id',                 sa.String(36),  nullable=False),
        sa.Column('member_name',               sa.String(200), nullable=False),
        sa.Column('member_email',              sa.String(255), nullable=True),
        sa.Column('tier',                      sa.Enum('explorer','active','elite','charter','corporate', name='membertier'), nullable=False),
        sa.Column('monthly_fee',               sa.Float(),     nullable=False),
        sa.Column('join_date',                 sa.Date(),      nullable=False),
        sa.Column('ltv_score',                 sa.Integer(),   nullable=False),
        sa.Column('predicted_ltv_12mo',        sa.Float(),     nullable=False),
        sa.Column('predicted_ltv_36mo',        sa.Float(),     nullable=False),
        sa.Column('historical_revenue',        sa.Float(),     nullable=False),
        sa.Column('churn_probability_30d',     sa.Float(),     nullable=False),
        sa.Column('churn_probability_60d',     sa.Float(),     nullable=False),
        sa.Column('churn_probability_90d',     sa.Float(),     nullable=False),
        sa.Column('churn_risk_band',           sa.Enum('safe','watch','at_risk','critical', name='churnriskband'), nullable=False),
        sa.Column('days_since_last_visit',     sa.Integer(),   nullable=False),
        sa.Column('visits_last_30d',           sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('visits_last_90d',           sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('avg_monthly_visits',        sa.Float(),     nullable=False, server_default='0'),
        sa.Column('feature_utilization_pct',   sa.Float(),     nullable=False, server_default='0'),
        sa.Column('nps_score',                 sa.Integer(),   nullable=True),
        sa.Column('upgrade_propensity',        sa.Enum('low','medium','high','very_high', name='upgradepropensity'), nullable=False, server_default='low'),
        sa.Column('upgrade_target_tier',       sa.Enum('explorer','active','elite','charter','corporate', name='membertier2'), nullable=True),
        sa.Column('last_scored_at',            sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('member_id'),
    )
    op.create_index('ix_ltv_risk_band',   'membership_ltv_scores', ['churn_risk_band'])
    op.create_index('ix_ltv_tier',        'membership_ltv_scores', ['tier'])
    op.create_index('ix_ltv_score',       'membership_ltv_scores', ['ltv_score'])
    op.create_index('ix_ltv_churn_30d',   'membership_ltv_scores', ['churn_probability_30d'])

    # ── Churn Predictions ─────────────────────────────────────────────────────
    op.create_table('churn_predictions',
        sa.Column('id',                        sa.String(36), nullable=False),
        sa.Column('member_id',                 sa.String(36), nullable=False),
        sa.Column('prediction_date',           sa.Date(),     nullable=False),
        sa.Column('churn_probability_30d',     sa.Float(),    nullable=False),
        sa.Column('churn_probability_60d',     sa.Float(),    nullable=False),
        sa.Column('churn_risk_band',           sa.Enum('safe','watch','at_risk','critical', name='churnriskband2'), nullable=False),
        sa.Column('feature_contributions',     sa.Text(),     nullable=True),
        sa.Column('created_at',                sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_churn_pred_member', 'churn_predictions', ['member_id'])
    op.create_index('ix_churn_pred_date',   'churn_predictions', ['prediction_date'])

    # ── Win-Back Sequences ────────────────────────────────────────────────────
    op.create_table('winback_sequences',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('ltv_score_id',    sa.String(36),  nullable=False),
        sa.Column('member_id',       sa.String(36),  nullable=False),
        sa.Column('member_name',     sa.String(200), nullable=False),
        sa.Column('tier',            sa.Enum('explorer','active','elite','charter','corporate', name='membertier3'), nullable=False),
        sa.Column('churn_risk_band', sa.Enum('safe','watch','at_risk','critical', name='churnriskband3'), nullable=False),
        sa.Column('revenue_at_risk', sa.Float(),     nullable=False),
        sa.Column('offer_type',      sa.String(100), nullable=False),
        sa.Column('offer_value',     sa.Float(),     nullable=False, server_default='0'),
        sa.Column('subject_line',    sa.String(300), nullable=False),
        sa.Column('message_body',    sa.Text(),      nullable=False),
        sa.Column('status',          sa.Enum('pending','sent','opened','converted','expired', name='winbackstatus'), nullable=False, server_default='pending'),
        sa.Column('scheduled_send',  sa.Date(),      nullable=True),
        sa.Column('sent_at',         sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at',       sa.DateTime(timezone=True), nullable=True),
        sa.Column('converted_at',    sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['ltv_score_id'], ['membership_ltv_scores.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_winback_status',    'winback_sequences', ['status'])
    op.create_index('ix_winback_member',    'winback_sequences', ['member_id'])

    # ── Membership Cohorts ────────────────────────────────────────────────────
    op.create_table('membership_cohorts',
        sa.Column('id',                  sa.String(36), nullable=False),
        sa.Column('cohort_label',        sa.String(50), nullable=False),
        sa.Column('tier',                sa.Enum('explorer','active','elite','charter','corporate', name='membertier4'), nullable=False),
        sa.Column('join_quarter',        sa.String(10), nullable=False),
        sa.Column('member_count',        sa.Integer(),  nullable=False),
        sa.Column('avg_ltv_score',       sa.Float(),    nullable=False),
        sa.Column('avg_churn_30d',       sa.Float(),    nullable=False),
        sa.Column('retention_rate_90d',  sa.Float(),    nullable=False),
        sa.Column('avg_monthly_revenue', sa.Float(),    nullable=False),
        sa.Column('created_at',          sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── Capital Sources ───────────────────────────────────────────────────────
    op.create_table('capital_sources',
        sa.Column('id',               sa.String(36),  nullable=False),
        sa.Column('phase',            sa.Enum('phase1','phase2','bridge', name='capitalphase'), nullable=False),
        sa.Column('source_type',      sa.Enum('community_bonds','bank_loan','sba_504','naming_rights','state_grant',
                                              'crowdfunding','equity','tid_bonds','operating_cash','irrrb_grant','mn_deed_grant',
                                              name='sourcetype'), nullable=False),
        sa.Column('label',            sa.String(200), nullable=False),
        sa.Column('target_amount',    sa.Float(),     nullable=False),
        sa.Column('committed_amount', sa.Float(),     nullable=False, server_default='0'),
        sa.Column('received_amount',  sa.Float(),     nullable=False, server_default='0'),
        sa.Column('deployed_amount',  sa.Float(),     nullable=False, server_default='0'),
        sa.Column('status',           sa.Enum('planning','application','committed','received','deployed','closed', name='sourcestatus'), nullable=False, server_default='planning'),
        sa.Column('interest_rate',    sa.Float(),     nullable=True),
        sa.Column('term_years',       sa.Integer(),   nullable=True),
        sa.Column('maturity_date',    sa.Date(),      nullable=True),
        sa.Column('lender_investor',  sa.String(200), nullable=True),
        sa.Column('contact_name',     sa.String(200), nullable=True),
        sa.Column('notes',            sa.Text(),      nullable=True),
        sa.Column('priority_order',   sa.Integer(),   nullable=False, server_default='99'),
        sa.Column('created_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',       sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cap_sources_phase',  'capital_sources', ['phase'])
    op.create_index('ix_cap_sources_status', 'capital_sources', ['status'])

    # ── Capital Disbursements ─────────────────────────────────────────────────
    op.create_table('capital_disbursements',
        sa.Column('id',              sa.String(36),  nullable=False),
        sa.Column('source_id',       sa.String(36),  nullable=True),
        sa.Column('phase',           sa.Enum('phase1','phase2','bridge', name='capitalphase2'), nullable=False),
        sa.Column('category',        sa.Enum('land','construction','equipment','ff_and_e','soft_costs',
                                             'working_capital','contingency','debt_service', name='disbcategory'), nullable=False),
        sa.Column('description',     sa.String(300), nullable=False),
        sa.Column('amount',          sa.Float(),     nullable=False),
        sa.Column('disbursed_date',  sa.Date(),      nullable=True),
        sa.Column('vendor',          sa.String(200), nullable=True),
        sa.Column('is_approved',     sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('notes',           sa.Text(),      nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cap_disb_phase',    'capital_disbursements', ['phase'])
    op.create_index('ix_cap_disb_category', 'capital_disbursements', ['category'])

    # ── Investor Reports ──────────────────────────────────────────────────────
    op.create_table('investor_reports',
        sa.Column('id',                      sa.String(36), nullable=False),
        sa.Column('report_period',           sa.String(20), nullable=False),
        sa.Column('report_type',             sa.String(50), nullable=False),
        sa.Column('total_capital_raised',    sa.Float(),    nullable=False),
        sa.Column('total_capital_deployed',  sa.Float(),    nullable=False),
        sa.Column('phase1_pct_complete',     sa.Float(),    nullable=False),
        sa.Column('phase2_pct_complete',     sa.Float(),    nullable=False),
        sa.Column('actual_irr',              sa.Float(),    nullable=True),
        sa.Column('projected_irr',           sa.Float(),    nullable=False),
        sa.Column('narrative',               sa.Text(),     nullable=True),
        sa.Column('created_at',              sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── TID Ledger ────────────────────────────────────────────────────────────
    op.create_table('tid_ledger',
        sa.Column('id',                    sa.String(36), nullable=False),
        sa.Column('month',                 sa.String(7),  nullable=False),
        sa.Column('hotel_room_revenue',    sa.Float(),    nullable=False),
        sa.Column('tid_assessment',        sa.Float(),    nullable=False),
        sa.Column('tid_cumulative',        sa.Float(),    nullable=False),
        sa.Column('rooms_sold',            sa.Integer(),  nullable=False),
        sa.Column('occupancy_pct',         sa.Float(),    nullable=False),
        sa.Column('tourism_visitors_est',  sa.Integer(),  nullable=False),
        sa.Column('created_at',            sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('month'),
    )
    op.create_index('ix_tid_month', 'tid_ledger', ['month'])


def downgrade() -> None:
    op.drop_table('tid_ledger')
    op.drop_table('investor_reports')
    op.drop_table('capital_disbursements')
    op.drop_table('capital_sources')
    op.drop_table('membership_cohorts')
    op.drop_table('winback_sequences')
    op.drop_table('churn_predictions')
    op.drop_table('membership_ltv_scores')
    for e in ['membertier','membertier2','membertier3','membertier4','churnriskband',
              'churnriskband2','churnriskband3','upgradepropensity','winbackstatus',
              'capitalphase','capitalphase2','sourcetype','sourcestatus','disbcategory']:
        op.execute(f'DROP TYPE IF EXISTS {e}')
