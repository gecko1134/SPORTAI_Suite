
import streamlit as st
import requests

def run():
    st.title("💬 Slack Alert Center")

    st.markdown("Configure and send custom alerts to your Slack channels using Incoming Webhooks.")

    message = st.text_area("Slack Message")
    webhook_url = st.text_input("Slack Webhook URL", type="password")

    if st.button("Send Alert"):
        if not message or not webhook_url:
            st.error("Both message and webhook URL are required.")
        else:
            try:
                response = requests.post(webhook_url, json={"text": message})
                if response.status_code == 200:
                    st.success("✅ Message sent to Slack!")
                else:
                    st.error(f"Slack returned {response.status_code}")
            except Exception as e:
                st.error(f"Error sending to Slack: {e}")
