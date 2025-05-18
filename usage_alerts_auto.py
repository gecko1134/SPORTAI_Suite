
import streamlit as st
from twilio.rest import Client

def run():
    st.title("📡 Surface Gap SMS Alerts")

    underused_surface = "Court 4"
    usage_pct = 43
    message = f"📉 {underused_surface} usage at {usage_pct}%. Recommend rental or promo."

    st.markdown(f"**Auto-detected:** {message}")

    phone = st.text_input("Admin Phone Number", "+15551234567")
    if st.button("Send SMS Alert"):
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
