
import streamlit as st

def run():
    st.title("🔗 Google Sheets Sync Setup")

    st.markdown("Use this to connect booking, sponsorship, or membership data to Google Sheets.")

    st.text_input("Google Sheet ID")
    st.text_input("Target Sheet Name")
    st.text_input("Service Account JSON Key (encrypted)")

    st.warning("⚠️ Ensure you’ve shared your Sheet with the service account email.")
    st.success("✅ Use gspread or pygsheets library to push/pull data after API setup.")
