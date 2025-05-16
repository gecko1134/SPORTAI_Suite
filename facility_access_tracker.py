import streamlit as st

def run():
    st.title("🔐 Facility Access Log")

    st.markdown("Last 5 Access Logs:")
    st.table([
        {"Member": "Jordan", "Method": "Phone QR", "Time": "7:02 AM"},
        {"Member": "Dana", "Method": "Fob", "Time": "9:45 AM"},
        {"Member": "Casey", "Method": "Phone QR", "Time": "5:30 PM"},
        {"Member": "Jordan", "Method": "Phone QR", "Time": "7:05 AM"},
        {"Member": "Guest", "Method": "Front Desk Manual", "Time": "12:00 PM"},
    ])