
import streamlit as st
from twilio.rest import Client

def run():
    st.title("👤 Member Activity Alerts")

    name = "Jordan Smith"
    inactivity_days = 35
    message = f"👤 Member {name} inactive for {inactivity_days} days. Send reactivation incentive."

    st.markdown(f"**Auto-detected:** {message}")

    phone = st.text_input("Marketing Contact Phone", "+15551234567")
    if st.button("Send Member Alert"):
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
