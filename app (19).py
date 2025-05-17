
import streamlit as st
from pathlib import Path
import importlib.util

# Load access control
access_control_path = Path(__file__).parent / "access_control.py"
spec = importlib.util.spec_from_file_location("access_control", access_control_path)
access_control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(access_control)

access_control.authenticate()

all_tabs = [
    "Sponsor Fulfillment Dashboard",
    "Contract Auto-Generator",
    "Sponsor Match Score Engine",
    "AI ROI Estimator",
    "AI Scheduling Optimizer",
    "Grant Tracker",
    "Facility Usage Tracker",
    "Sponsor Fulfillment PDF Generator",
    "Sponsor Portal Login",
    "AI Bundle Builder",
    "AI Pricing Engine",
    "Credit Usage Tracker",
    "Calendar Booking with Credit Check",
    "Board of Directors Dashboard",
    "Team & Tournament Tracker",
    "Team Loyalty Credit System",
    "Redemption Tracker",
    "Voucher Email Sender",
    "Redemption Reporting",
    "Referee & Volunteer Tracker",
    "Financial Pro Forma Dashboard",
    "AI Forecast & Suggestions",
    "Contract Conversion Alerts"
]

role = st.session_state["user_role"]
accessible_tabs = all_tabs if access_control.get_accessible_tabs() == "all" else [
    tab for tab in all_tabs if tab in access_control.get_accessible_tabs()
]

st.set_page_config(page_title="Unified Admin Dashboard", layout="wide")
st.sidebar.title("🏟️ Complex Admin Dashboard")
tab = st.sidebar.selectbox("Choose Module", accessible_tabs)

def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base_path = Path(__file__).parent
modules = {
    "Sponsor Fulfillment Dashboard": "sponsor_fulfillment_dashboard.py",
    "Contract Auto-Generator": "contract_auto_generator.py",
    "Sponsor Match Score Engine": "ai_sponsor_match_score.py",
    "AI ROI Estimator": "ai_roi_estimator.py",
    "AI Scheduling Optimizer": "ai_scheduling_optimizer.py",
    "Grant Tracker": "enhanced_grant_tracker.py",
    "Facility Usage Tracker": "usage_tracker.py",
    "Sponsor Fulfillment PDF Generator": "sponsor_fulfillment_pdf_generator.py",
    "Sponsor Portal Login": "sponsor_portal_login.py",
    "AI Bundle Builder": "ai_bundle_builder.py",
    "AI Pricing Engine": "ai_pricing_engine.py",
    "Credit Usage Tracker": "credit_usage_tracker.py",
    "Calendar Booking with Credit Check": "calendar_booking_credit_check.py",
    "Board of Directors Dashboard": "board_of_directors_dashboard.py",
    "Team & Tournament Tracker": "team_tournament_tracker.py",
    "Team Loyalty Credit System": "team_loyalty_credit_system.py",
    "Redemption Tracker": "redemption_tracker.py",
    "Voucher Email Sender": "voucher_email_sender.py",
    "Redemption Reporting": "redemption_reporting.py",
    "Referee & Volunteer Tracker": "ref_volunteer_tracker.py",
    "Financial Pro Forma Dashboard": "financial_proforma_dashboard.py",
    "AI Forecast & Suggestions": "ai_forecast_suggestion.py",
    "Contract Conversion Alerts": "contract_conversion_alerts.py"
}

if tab in modules:
    module = load_module(tab.replace(" ", "_").lower(), base_path / modules[tab])
    module.run()
