import streamlit as st
import auth
import weekly_report_generator
import team_club_manager
import volunteer_hub
import setup_assistant_ai
import scholarship_tracker
import sponsor_dashboard
import sponsorship_inventory_manager
import sponsorship_ai_calculator
import student_committee
import visual_calendar_layout
import sponsorship_roi_tracker
import sponsorship_availability
import sponsorship_contract_generator
import sponsorship_tracker
import pdf_export_tool
import proposal_to_pdf
import report_download_portal
import referee_manager
import revenue_heatmap
import scholarship_fund_manager
import membership_loyalty_rewards
import membership_marketing_ai
import memberships_tool
import membership_ticketing_integration
import mentorship_center
import pandadoc_contract
import nil_tracker
import mobile_friendly_ui
import revenue_proforma_auto
import league_coordinator
import governance_tool
import membership_credit_tracker
import marketing_flipbook_generator
import membership_goal_tracker
import membership_insights_ai
import dynamic_pricing_tool
import email_notifications
import event_control_panel
import event_creator_ai
import facility_access_tracker
import facility_master_tracker
import facility_contract_monitor
import facility_membership_comparator_ai
import flipbook_embedder
import facility_membership_monitor
import ai_scheduler_tool
import membership_crm_tracker
import ai_scheduling_suggestions
import auth
import google_sheets_sync
import central_dashboard
import complex_usage_optimizer
import contract_insights_ai
import contract_usage_tracker
import dome_usage_tool
import performance_goal_ai

TOOLS = {
    "Weekly Report Generator": weekly_report_generator,
    "Team Club Manager": team_club_manager,
    "Volunteer Hub": volunteer_hub,
    "Setup Assistant Ai": setup_assistant_ai,
    "Scholarship Tracker": scholarship_tracker,
    "Sponsor Dashboard": sponsor_dashboard,
    "Sponsorship Inventory Manager": sponsorship_inventory_manager,
    "Sponsorship Ai Calculator": sponsorship_ai_calculator,
    "Student Committee": student_committee,
    "Visual Calendar Layout": visual_calendar_layout,
    "Sponsorship Roi Tracker": sponsorship_roi_tracker,
    "Sponsorship Availability": sponsorship_availability,
    "Sponsorship Contract Generator": sponsorship_contract_generator,
    "Sponsorship Tracker": sponsorship_tracker,
    "Pdf Export Tool": pdf_export_tool,
    "Proposal To Pdf": proposal_to_pdf,
    "Report Download Portal": report_download_portal,
    "Referee Manager": referee_manager,
    "Revenue Heatmap": revenue_heatmap,
    "Scholarship Fund Manager": scholarship_fund_manager,
    "Membership Loyalty Rewards": membership_loyalty_rewards,
    "Membership Marketing Ai": membership_marketing_ai,
    "Memberships Tool": memberships_tool,
    "Membership Ticketing Integration": membership_ticketing_integration,
    "Mentorship Center": mentorship_center,
    "Pandadoc Contract": pandadoc_contract,
    "Nil Tracker": nil_tracker,
    "Mobile Friendly Ui": mobile_friendly_ui,
    "Revenue Proforma Auto": revenue_proforma_auto,
    "League Coordinator": league_coordinator,
    "Governance Tool": governance_tool,
    "Membership Credit Tracker": membership_credit_tracker,
    "Marketing Flipbook Generator": marketing_flipbook_generator,
    "Membership Goal Tracker": membership_goal_tracker,
    "Membership Insights Ai": membership_insights_ai,
    "Dynamic Pricing Tool": dynamic_pricing_tool,
    "Email Notifications": email_notifications,
    "Event Control Panel": event_control_panel,
    "Event Creator Ai": event_creator_ai,
    "Facility Access Tracker": facility_access_tracker,
    "Facility Master Tracker": facility_master_tracker,
    "Facility Contract Monitor": facility_contract_monitor,
    "Facility Membership Comparator Ai": facility_membership_comparator_ai,
    "Flipbook Embedder": flipbook_embedder,
    "Facility Membership Monitor": facility_membership_monitor,
    "Ai Scheduler Tool": ai_scheduler_tool,
    "Membership Crm Tracker": membership_crm_tracker,
    "Ai Scheduling Suggestions": ai_scheduling_suggestions,
    "Auth": auth,
    "Google Sheets Sync": google_sheets_sync,
    "Central Dashboard": central_dashboard,
    "Complex Usage Optimizer": complex_usage_optimizer,
    "Contract Insights Ai": contract_insights_ai,
    "Contract Usage Tracker": contract_usage_tracker,
    "Dome Usage Tool": dome_usage_tool,
    "Performance Goal Ai": performance_goal_ai
}

def run():
    st.set_page_config(page_title='Venture North Admin', layout='wide')
    st.sidebar.title('🧭 Select Tool')
    selection = st.sidebar.selectbox('Choose a Tool', list(TOOLS.keys()))
    TOOLS[selection].run()

run()