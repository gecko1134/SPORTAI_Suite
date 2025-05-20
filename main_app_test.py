import streamlit as st
import auth
import ai_scheduler_tool
import ai_scheduling_suggestions
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
import facility_access_tracker
import facility_contract_monitor
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
import membership_goal_tracker
import membership_insights_ai
import membership_loyalty_rewards
import membership_marketing_ai
import membership_ticketing_integration
import memberships_tool
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
import student_committee
import team_club_manager
import visual_calendar_layout
import volunteer_hub
import weekly_report_generator

TOOLS = {
    "Ai Scheduler Tool": ai_scheduler_tool,
    "Ai Scheduling Suggestions": ai_scheduling_suggestions,
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
    "Facility Access Tracker": facility_access_tracker,
    "Facility Contract Monitor": facility_contract_monitor,
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
    "Membership Goal Tracker": membership_goal_tracker,
    "Membership Insights Ai": membership_insights_ai,
    "Membership Loyalty Rewards": membership_loyalty_rewards,
    "Membership Marketing Ai": membership_marketing_ai,
    "Membership Ticketing Integration": membership_ticketing_integration,
    "Memberships Tool": memberships_tool,
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
    "Student Committee": student_committee,
    "Team Club Manager": team_club_manager,
    "Visual Calendar Layout": visual_calendar_layout,
    "Volunteer Hub": volunteer_hub,
    "Weekly Report Generator": weekly_report_generator
}

def run():
    st.set_page_config(page_title='Venture North Admin', layout='wide')
    st.sidebar.title('🧭 Select Tool')
    selection = st.sidebar.selectbox('Choose a Tool', list(TOOLS.keys()))
    TOOLS[selection].run()

run()
