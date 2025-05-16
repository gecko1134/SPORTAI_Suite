import streamlit as st
import json
import auth

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

def run():
    st.set_page_config(page_title='Venture North Admin', layout='wide')
    if 'user' not in st.session_state or not st.session_state.user:
        login()
        return
    user = st.session_state.user
    role = user['role']
    st.sidebar.success(f"Logged in as {user['email']} ({role})")
    logout()

    TOOLS = {
        # ADMIN TOOLS
        # BOARD TOOLS
        # SPONSOR TOOLS
        # MEMBER TOOLS
    }

    options = [k for k in TOOLS if k in TOOLS]  # role already filters above
    selection = st.sidebar.selectbox('Choose a Tool', options)
    TOOLS[selection].run()

run()