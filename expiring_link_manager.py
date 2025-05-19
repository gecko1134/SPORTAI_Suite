
import streamlit as st
from datetime import datetime, timedelta

def run():
    st.title("🕒 Expiring Link Generator")

    recipient = st.text_input("Recipient Name", "Jordan Smith")
    link_type = st.selectbox("Link Type", ["Proposal", "Sponsor Portal", "Pitch Deck"])
    days_valid = st.slider("Valid for how many days?", 1, 30, 7)

    base_link = {
        "Proposal": "https://yourdomain.com/proposals/",
        "Sponsor Portal": "https://yourdomain.com/sponsor-portal",
        "Pitch Deck": "https://flippingbook.com/your-deck"
    }[link_type]

    expires = datetime.now() + timedelta(days=days_valid)
    token = f"{recipient.lower().replace(' ', '')}-{int(expires.timestamp())}"
    link = f"{base_link}?token={token}"

    st.code(link)
    st.caption(f"Expires on {expires.strftime('%Y-%m-%d %H:%M')}")

    st.download_button("📋 Copy Expiring Link", link.encode(), file_name=f"{recipient}_expiring_link.txt")
