
import streamlit as st
from twilio.rest import Client

def run():
    st.title("🧍 Credential Expiry Alerts")

    name = "Dana K."
    role = "Referee"
    exp_date = "2024-07-01"
    message = f"🧍 {role} {name}'s certification expires on {exp_date}. Notify for recertification."

    st.markdown(f"**Auto-detected:** {message}")

    phone = st.text_input("Ops Contact Phone", "+15551234567")
    if st.button("Send Credential Alert"):
        try:
            client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
            client.messages.create(
                body=message,
                from_=st.secrets["TWILIO_PHONE_NUMBER"],
                to=phone
            )
            st.success("✅ Alert sent!")
        except Exception as e:
            st.error(f"Error: {e}")
