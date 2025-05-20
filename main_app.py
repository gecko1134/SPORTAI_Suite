

import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai_modules.demand_forecasting import DemandForecaster
from ai_modules.scheduling_optimizer import optimize_schedule
from ai_modules.sponsorship_matcher import match_sponsors
from ai_modules.dynamic_contract_generator import generate_contract
from ai_modules.membership_churn import ChurnPredictor
from ai_modules.marketing_optimizer import optimize_campaign


import optimize_schedule
import match_sponsors
import generate_contract
import ChurnPredictor
import optimize_campaign
import member_selector
import auto_contract_generator
import header_loader
import fundraising_launch_center
import grant_renewal_manager
import investor_kit_generator
import board_packet_pdf_generator
import funding_narrative_sync
import crm_pipeline_dashboard
import board_report_scheduler
import hubspot_deal_logger
import sponsor_pitch_portal
import mailchimp_lead_collector
import marketing_packet_builder
import screen_rotation_scheduler
import media_display_rotator
import investor_pitch_portal
import admin_override_console
import expiring_link_manager
import sponsor_link_sender
import flipbook_pitch_creator
import sponsor_pdf_packet
import sponsor_pitchbook_builder
import sponsor_proposal_pdf
import ai_sponsor_pricing_trends
import sponsorship_inventory_limiter
import crm_grant_donor_sync
import pdf_grant_exporter
import grant_alert_center
import grant_writer_ai
import grant_match_ai
import grant_status_manager
import donation_landing_page
import crm_export_generator
import donation_checkout
import donation_campaign_viewer
import donor_match_ai
import donor_message_builder
import donor_profile_creator
import donation_goal_tracker
import portal_router
import upsell_offer_engine
import member_portal
import sponsor_portal
import public_schedule
import sponsor_map_viewer
import ai_facility_chat
import slack_alert_center
import webhook_automation
import admin_sidebar_badges
import daily_task_scheduler
import ai_voice_responder
import member_alerts_auto
import credential_expiry_alerts
import usage_alerts_auto
import contract_alerts_auto
import platform_guidebook_writer
import board_pdf_exporter
import finance_feed_connector
import board_financial_summary
import revenue_projection_simulator
import sponsorship_revenue_builder
import event_admin
import surface_usage_by_type
import governance_admin
import governance_diagram
import financial_feed_sync
import sms_alert_center
import real_time_dashboard
import gsheets_sync
import event_profit_analyzer
import adaptive_use_planner
import park_activity_dashboard
import surface_demand_heatmap
import tournament_scheduler
import international_team_portal
import esports_manager
import adaptive_sports_center
import streamlit as st
import json
import auth
import ai_event_forecast
import ai_matchmaker_tool
import ai_revenue_maximizer
import ai_scheduler_tool
import ai_scheduling_suggestions
import ai_sponsor_opportunity_finder
import ai_strategy_dashboard
import ai_suggestion_digest
import ai_voice_command
import auth
import central_dashboard
import complex_usage_optimizer
import contract_insights_ai
import contract_usage_tracker
import dome_usage_tool
import dynamic_pricing_tool
import email_notifications
import event_control_panel
import event_creator_ai
import event_types_config
import facility_access_tracker
import facility_capacity_alerts
import facility_contract_monitor
import facility_layout_map
import facility_master_tracker
import facility_membership_comparator_ai
import facility_membership_monitor
import flipbook_embedder
import google_sheets_sync
import governance_tool
import league_coordinator
import marketing_flipbook_generator
import membership_credit_tracker
import membership_crm_tracker
import membership_dashboard
import membership_goal_tracker
import membership_insights_ai
import membership_loyalty_rewards
import membership_marketing_ai
import membership_ticketing_integration
import mentorship_center
import mobile_friendly_ui
import nil_tracker
import pandadoc_contract
import pdf_export_tool
import performance_goal_ai
import proposal_to_pdf
import referee_manager
import report_download_portal
import revenue_heatmap
import revenue_proforma_auto
import scholarship_fund_manager
import scholarship_tracker
import setup_assistant_ai
import sponsor_dashboard
import sponsorship_ai_calculator
import sponsorship_availability
import sponsorship_contract_generator
import sponsorship_inventory_manager
import sponsorship_roi_tracker
import sponsorship_tracker
import sport_library
import student_committee
import team_club_manager
import trail_access_planner
import visual_calendar_layout
import volunteer_hub
import weekly_report_generator
import investor_pitch_portal
import admin_override_console




with open('users.json') as f:
    users = json.load(f)

def login():
    st.sidebar.header('🔐 Login')
    email = st.sidebar.text_input('Email')
    password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.button('Login'):
        user = users.get(email)
        if user and user['password'] == password:
            st.session_state.user = {'email': email, 'role': user['role']}
        else:
            st.sidebar.error('Invalid credentials.')

def logout():
    if st.sidebar.button('Logout'):
        st.session_state.user = None

TOOLS = {
    "Ai Event Forecast": ai_event_forecast,
    "Ai Matchmaker Tool": ai_matchmaker_tool,
    "Ai Revenue Maximizer": ai_revenue_maximizer,
    "Ai Scheduler Tool": ai_scheduler_tool,
    "Ai Scheduling Suggestions": ai_scheduling_suggestions,
    "Ai Sponsor Opportunity Finder": ai_sponsor_opportunity_finder,
    "Ai Strategy Dashboard": ai_strategy_dashboard,
    "Ai Suggestion Digest": ai_suggestion_digest,
    "Ai Voice Command": ai_voice_command,
    "Auth": auth,
    "Central Dashboard": central_dashboard,
    "Complex Usage Optimizer": complex_usage_optimizer,
    "Contract Insights Ai": contract_insights_ai,
    "Contract Usage Tracker": contract_usage_tracker,
    "Dome Usage Tool": dome_usage_tool,
    "Dynamic Pricing Tool": dynamic_pricing_tool,
    "Email Notifications": email_notifications,
    "Event Control Panel": event_control_panel,
    "Event Creator Ai": event_creator_ai,
    "Event Types Config": event_types_config,
    "Facility Access Tracker": facility_access_tracker,
    "Facility Capacity Alerts": facility_capacity_alerts,
    "Facility Contract Monitor": facility_contract_monitor,
    "Facility Layout Map": facility_layout_map,
    "Facility Master Tracker": facility_master_tracker,
    "Facility Membership Comparator Ai": facility_membership_comparator_ai,
    "Facility Membership Monitor": facility_membership_monitor,
    "Flipbook Embedder": flipbook_embedder,
    "Google Sheets Sync": google_sheets_sync,
    "Governance Tool": governance_tool,
    "League Coordinator": league_coordinator,
    "Marketing Flipbook Generator": marketing_flipbook_generator,
    "Membership Credit Tracker": membership_credit_tracker,
    "Membership Crm Tracker": membership_crm_tracker,
    "Membership Dashboard": membership_dashboard,
    "Membership Goal Tracker": membership_goal_tracker,
    "Membership Insights Ai": membership_insights_ai,
    "Membership Loyalty Rewards": membership_loyalty_rewards,
    "Membership Marketing Ai": membership_marketing_ai,
    "Membership Ticketing Integration": membership_ticketing_integration,
    "Mentorship Center": mentorship_center,
    "Mobile Friendly Ui": mobile_friendly_ui,
    "Nil Tracker": nil_tracker,
    "Pandadoc Contract": pandadoc_contract,
    "Pdf Export Tool": pdf_export_tool,
    "Performance Goal Ai": performance_goal_ai,
    "Proposal To Pdf": proposal_to_pdf,
    "Referee Manager": referee_manager,
    "Report Download Portal": report_download_portal,
    "Revenue Heatmap": revenue_heatmap,
    "Revenue Proforma Auto": revenue_proforma_auto,
    "Scholarship Fund Manager": scholarship_fund_manager,
    "Scholarship Tracker": scholarship_tracker,
    "Setup Assistant Ai": setup_assistant_ai,
    "Sponsor Dashboard": sponsor_dashboard,
    "Sponsorship Ai Calculator": sponsorship_ai_calculator,
    "Sponsorship Availability": sponsorship_availability,
    "Sponsorship Contract Generator": sponsorship_contract_generator,
    "Sponsorship Inventory Manager": sponsorship_inventory_manager,
    "Sponsorship Roi Tracker": sponsorship_roi_tracker,
    "Sponsorship Tracker": sponsorship_tracker,
    "Sport Library": sport_library,
    "Student Committee": student_committee,
    "Team Club Manager": team_club_manager,
    "Trail Access Planner": trail_access_planner,
    "Visual Calendar Layout": visual_calendar_layout,
    "Volunteer Hub": volunteer_hub,
    "Weekly Report Generator": weekly_report_generator,
    "Esports Manager": esports_manager,
    "Adaptive Sports Center": adaptive_sports_center,
    "Tournament Scheduler": tournament_scheduler,
    "International Team Portal": international_team_portal,
    "Park Activity Dashboard": park_activity_dashboard,
    "Surface Demand Heatmap": surface_demand_heatmap,
    "Event Profitability Analyzer": event_profit_analyzer,
    "Adaptive Use Planner": adaptive_use_planner,
    "Real-Time Dashboard": real_time_dashboard,
    "Google Sheets Sync": gsheets_sync,
    "SMS Alert Center": sms_alert_center,
    "Event Admin": event_admin,
    "Surface Usage by Type": surface_usage_by_type,
    "Governance Admin": governance_admin,
    "Governance Diagram": governance_diagram,
    "Financial Feed Sync": financial_feed_sync,
    "Revenue Projection Simulator": revenue_projection_simulator,
    "Sponsorship Revenue Builder": sponsorship_revenue_builder,
    "Board Financial Summary": board_financial_summary,
    "Board PDF Exporter": board_pdf_exporter,
    "Finance Feed Connector": finance_feed_connector,
    "Platform Guidebook": platform_guidebook_writer,
    "Surface Gap Alerts": usage_alerts_auto,
    "Sponsor Contract Alerts": contract_alerts_auto,
    "Member Alerts Auto": member_alerts_auto,
    "Credential Expiry Alerts": credential_expiry_alerts,
    "Daily Task Scheduler": daily_task_scheduler,
    "Voice Assistant": ai_voice_responder,
    "Admin Sidebar Badges": admin_sidebar_badges,
    "Slack Alert Center": slack_alert_center,
    "Webhook Automation": webhook_automation,
    "AI Facility Chat": ai_facility_chat,
    "Public Schedule": public_schedule,
    "Sponsor Map Viewer": sponsor_map_viewer,
    "Member Portal": member_portal,
    "Sponsor Portal": sponsor_portal,
    "Portal Router": portal_router,
    "Upsell Offer Engine": upsell_offer_engine,
    "Donor Profile Creator": donor_profile_creator,
    "Donation Goal Tracker": donation_goal_tracker,
    "Donor Match AI": donor_match_ai,
    "Donor Message Builder": donor_message_builder,
    "Donation Checkout": donation_checkout,
    "Donation Campaign Viewer": donation_campaign_viewer,
    "Public Donation Page": donation_landing_page,
    "CRM Export Builder": crm_export_generator,
    "AI Grant Match": grant_match_ai,
    "Grant Status Tracker": grant_status_manager,
    "Grant Alerts": grant_alert_center,
    "AI Grant Writer": grant_writer_ai,
    "CRM Sync (Grants & Donors)": crm_grant_donor_sync,
    "PDF Grant Exporter": pdf_grant_exporter,
    "AI Sponsor Pricing Trends": ai_sponsor_pricing_trends,
    "Sponsor Inventory Limits": sponsorship_inventory_limiter,
    "AI Sponsorship Pitchbook": sponsor_pitchbook_builder,
    "Sponsor Proposal PDF": sponsor_proposal_pdf,
    "Flipbook Pitch Creator": flipbook_pitch_creator,
    "Sponsor Packet PDF": sponsor_pdf_packet,
    "Sponsor Link Generator": sponsor_link_generator,
    "Expiring Link Generator": expiring_link_manager,
    "Sponsor Link Sender": sponsor_link_sender,
    "Investor Portal": investor_pitch_portal,
    "Admin Override Console": admin_override_console,
    "Investor Portal": investor_pitch_portal,
    "Admin Override Console": admin_override_console,
    "Screen Scheduler": screen_rotation_scheduler,
    "Media Rotator": media_display_rotator,
    "Marketing Packet Builder": marketing_packet_builder,
    "Sponsor Pitch Portal": sponsor_pitch_portal,
    "Mailchimp Lead Collector": mailchimp_lead_collector,
    "HubSpot Deal Logger": hubspot_deal_logger,
    "CRM Pipeline Dashboard": crm_pipeline_dashboard,
    "Board Report Scheduler": board_report_scheduler,
    "Board Packet Generator": board_packet_pdf_generator,
    "Fundraising Narrative Sync": funding_narrative_sync,
    "Grant Renewal Tracker": grant_renewal_manager,
    "Investor Kit Generator": investor_kit_generator,
    "Fundraising Launch Center": fundraising_launch_center,
    "Membership Recommender": member_selector,
    "Contract Generator": auto_contract_generator,
}

def run():
    st.set_page_config(page_title='Venture North Admin', layout='wide')
    if 'user' not in st.session_state or not st.session_state.user:
        login()
        return
    user = st.session_state.user
    st.sidebar.success(f"Logged in as {user['email']} ({user['role']})")
    logout()
    selection = st.sidebar.selectbox('Choose a Tool', list(TOOLS.keys()))
    if selection in TOOLS:
        TOOLS[selection].run()
        header_loader.run()
        st.sidebar.title('AI Optimizations')

if st.sidebar.button('Forecast Demand'):
    st.write('Demand Forecast:')
    # TODO: load booking_data.csv and call DemandForecaster.predict()

if st.sidebar.button('Optimize Schedule'):
    st.write('Optimized Schedule:')
    # TODO: load schedule_requests.csv, resources.json, call optimize_schedule()

if st.sidebar.button('Match Sponsors'):
    st.write('Sponsor Matches:')
    # TODO: load assets.csv and sponsors.csv, call match_sponsors()

if st.sidebar.button('Generate Dynamic Contract'):
    st.write('Contract Link:')
    # TODO: call generate_contract(template_id, data, api_key) and show URL

if st.sidebar.button('Predict Churn'):
    st.write('Churn Risk Scores:')
    # TODO: load member_features.csv, call ChurnPredictor.predict()

if st.sidebar.button('Optimize Campaign'):
    st.write('Campaign Result:')
    # TODO: load invites.csv, call optimize_campaign()

st.title('SportAI Suite with AI Modules')
st.write('Select an AI tool from the sidebar to get started.')

run()
