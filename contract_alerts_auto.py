
import streamlit as st
from twilio.rest import Client

def run():
    st.title("📢 Sponsor Contract Alerts")

    sponsor = "BankCo"
    asset = "Scoreboard"
    days_left = 12
    message = f"📢 {sponsor}'s {asset} contract expires in {days_left} days."

    st.markdown(f"**Auto-detected:** {message}")

    phone = st.text_input("Sponsorship Manager Phone", "+15551234567")
    if st.button("Send Contract Alert"):
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
