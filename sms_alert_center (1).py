import streamlit as st
from twilio.rest import Client

def run():
    st.title("📲 SMS Alert Center – Twilio Enabled")

    alert_type = st.selectbox("Alert Type", ["Surface Gap", "Expiring Contract", "Member Inactivity"])
    phone = st.text_input("Phone Number (e.g. +15551234567)", "+15551234567")

    if alert_type == "Surface Gap":
        message = "⚠️ Surface availability: Court 3 open Saturday 2–4pm."
    elif alert_type == "Expiring Contract":
        message = "📢 Contract expiring: BankCo - Scoreboard ends in 10 days."
    elif alert_type == "Member Inactivity":
        message = "👤 Member Jordan Smith inactive 30+ days. Suggest reactivation."

    st.code(f"TO: {phone}\n\n{message}", language="markdown")

    if st.button("Send SMS Now"):
        try:
            client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
            sent = client.messages.create(
                body=message,
                from_=st.secrets["TWILIO_PHONE_NUMBER"],
                to=phone
            )
            st.success("✅ SMS sent successfully!")
        except Exception as e:
            st.error(f"Failed to send SMS: {e}")