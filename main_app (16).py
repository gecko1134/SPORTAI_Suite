
import streamlit as st
import json
import auth

# Load users
with open("users.json") as f:
    users = json.load(f)

# Login function
def login():
    st.sidebar.header("🔐 Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")
    if login_btn:
        user = users.get(email)
        if user and user["password"] == password:
            st.session_state.user = {"email": email, "role": user["role"]}
        else:
            st.sidebar.error("Invalid credentials.")

# Logout function
def logout():
    if st.sidebar.button("Logout"):
        st.session_state.user = None

# Secure tool runner
def run():
    st.set_page_config(page_title="Venture North Admin", layout="wide")
    if "user" not in st.session_state or not st.session_state.user:
        login()
        return

    st.sidebar.success(f"Logged in as {st.session_state.user['email']} ({st.session_state.user['role']})")
    logout()

    # Tool imports
    import sponsorship_ai_calculator
    import memberships_tool
    import central_dashboard
    import event_creator_ai
    import flipbook_embedder
    import revenue_heatmap
    import revenue_proforma_auto
    import weekly_report_generator
    import report_download_portal
    import pdf_export_tool
    import membership_crm_tracker
    import membership_goal_tracker
    import membership_ticketing_integration
    import performance_goal_ai

    TOOLS = {
        "📊 Dashboard": central_dashboard,
        "👥 Memberships": memberships_tool,
        "📋 Member CRM": membership_crm_tracker,
        "🎯 Membership Goals": membership_goal_tracker,
        "🎟 Ticketing Log": membership_ticketing_integration,
        "💼 Sponsorship AI": sponsorship_ai_calculator,
        "🎉 Create Event": event_creator_ai,
        "📈 Revenue Heatmap": revenue_heatmap,
        "🧾 Pro Forma Summary": revenue_proforma_auto,
        "📥 Flipbook Viewer": flipbook_embedder,
        "🗓 Weekly Reports": weekly_report_generator,
        "📤 Download Reports": report_download_portal,
        "📄 Export to PDF": pdf_export_tool,
        "📌 Performance Goals": performance_goal_ai
    }

    st.sidebar.title("🧭 Tools Menu")
    selection = st.sidebar.selectbox("Choose a Tool", list(TOOLS.keys()))
    TOOLS[selection].run()

run()
