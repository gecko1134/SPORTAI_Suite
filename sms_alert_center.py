import streamlit as st

def run():
    st.title("📲 SMS Alert Center")

    st.markdown("Use this module to configure and preview real-time alert messages.")

    alert_type = st.selectbox("Alert Type", ["Surface Gap", "Expiring Contract", "Member Inactivity"])
    phone = st.text_input("Phone Number (e.g. +15551234567)", "+15551234567")

    if alert_type == "Surface Gap":
        message = "⚠️ Surface availability: Court 3 open Saturday 2–4pm."
    elif alert_type == "Expiring Contract":
        message = "📢 Contract expiring: BankCo - Scoreboard ends in 10 days."
    elif alert_type == "Member Inactivity":
        message = "👤 Member Jordan Smith inactive 30+ days. Suggest reactivation."

    if phone:
        st.markdown("### Preview")
        st.code(f"TO: {phone}\n\n{message}", language="markdown")

    st.success("✅ Message preview generated. Twilio API can send this via REST client.")