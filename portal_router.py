
import streamlit as st
import member_portal
import sponsor_portal
import central_dashboard  # default for admin/board

def run():
    st.title("🔐 Role-Based Portal Router")

    role = st.session_state.get("user", {}).get("role", "guest")

    if role == "member":
        member_portal.run()
    elif role == "sponsor":
        sponsor_portal.run()
    else:
        central_dashboard.run()
