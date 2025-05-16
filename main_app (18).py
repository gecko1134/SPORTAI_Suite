import streamlit as st
import json
import auth
import central_dashboard
import memberships_tool
import sponsorship_ai_calculator

with open('users.json') as f:
    users = json.load(f)

ROLE_TOOLS = {
    'admin': {
        'Dashboard': central_dashboard,
        'Memberships': memberships_tool,
        'Sponsorship Ai': sponsorship_ai_calculator,
    },
    'board': {
        'Dashboard': central_dashboard,
        'Memberships': memberships_tool,
        'Sponsorship Ai': sponsorship_ai_calculator,
    },
    'sponsor': {
        'Dashboard': central_dashboard,
        'Memberships': memberships_tool,
        'Sponsorship Ai': sponsorship_ai_calculator,
    },
    'member': {
        'Dashboard': central_dashboard,
        'Memberships': memberships_tool,
        'Sponsorship Ai': sponsorship_ai_calculator,
    },
}

def login():
    st.sidebar.header("🔐 Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = users.get(email)
        if user and user["password"] == password:
            st.session_state.user = {"email": email, "role": user["role"]}
        else:
            st.sidebar.error("Invalid credentials.")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.user = None

def run():
    st.set_page_config(page_title="Venture North Admin", layout="wide")
    if "user" not in st.session_state or not st.session_state.user:
        login()
        return

    user = st.session_state.user
    role = user["role"]
    st.sidebar.success(f"Logged in as {user['email']} ({role})")
    logout()

    TOOLS = ROLE_TOOLS.get(role, {})
    if not TOOLS:
        st.warning("No tools assigned for this role.")
        return

    selection = st.sidebar.selectbox("Choose a Tool", list(TOOLS.keys()))
    if selection in TOOLS:
        TOOLS[selection].run()
    else:
        st.warning("Tool not found.")
run()
