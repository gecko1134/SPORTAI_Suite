import streamlit as st
import json
import auth
import central_dashboard
import complex_usage_optimizer
import sponsorship_inventory_manager

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
    "Central Dashboard": central_dashboard,
    "Complex Usage Optimizer": complex_usage_optimizer,
    "Sponsorship Inventory Manager": sponsorship_inventory_manager
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