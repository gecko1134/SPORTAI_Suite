import ai_sponsor_opportunity_finder
...
"AI Sponsor Opportunity Finder": ai_sponsor_opportunity_finder,
import streamlit as st
import json
import auth
import ai_matchmaker_tool
import ai_scheduler_tool
import ai_scheduling_suggestions
import auth
import central_dashboard
import complex_usage_optimizer

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
    "Ai Matchmaker Tool": ai_matchmaker_tool,
    "Ai Scheduler Tool": ai_scheduler_tool,
    "Ai Scheduling Suggestions": ai_scheduling_suggestions,
    "Auth": auth,
    "Central Dashboard": central_dashboard,
    "Complex Usage Optimizer": complex_usage_optimizer
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

run()
