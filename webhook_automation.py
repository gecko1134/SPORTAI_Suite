
import streamlit as st
import requests

def run():
    st.title("🔄 Webhook Automation Tool")

    st.markdown("Send data to external systems like Zapier, Airtable, or Google Sheets.")

    endpoint = st.text_input("Webhook URL", type="password")
    payload = st.text_area("JSON Payload", value='{"event": "new_member", "name": "Jordan Smith", "tier": "Gold"}')

    if st.button("Send Webhook"):
        try:
            result = requests.post(endpoint, json=eval(payload))
            if result.status_code == 200:
                st.success("✅ Webhook sent successfully!")
            else:
                st.error(f"Failed: {result.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")
