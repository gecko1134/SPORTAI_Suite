
import streamlit as st
import requests
from twilio.rest import Client

def run():
    st.title("📤 Smart Sponsor Link Sender")

    method = st.selectbox("Send Via", ["SMS (Twilio)", "Slack Webhook"])
    recipient = st.text_input("Recipient Name", "Jordan Smith")
    phone_or_webhook = st.text_input("Phone # or Webhook URL")
    link = st.text_input("Paste Link", "https://yourdomain.com/proposal")

    if st.button("Send Link"):
        try:
            if method == "SMS (Twilio)":
                client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
                message = client.messages.create(
                    body=f"Hi {recipient}, here’s your sponsorship link: {link}",
                    from_=st.secrets["TWILIO_PHONE_NUMBER"],
                    to=phone_or_webhook
                )
                st.success("✅ SMS sent!")
            elif method == "Slack Webhook":
                response = requests.post(phone_or_webhook, json={"text": f"{recipient}, view your link: {link}"})
                if response.status_code == 200:
                    st.success("✅ Slack message sent!")
                else:
                    st.error(f"Slack Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error sending message: {e}")
