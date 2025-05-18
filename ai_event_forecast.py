
import streamlit as st
import datetime

def run():
    st.title("📆 AI Event Forecast & Traffic Outlook")

    today = datetime.date.today()
    st.subheader(f"Today: {today.strftime('%A, %B %d')}")

    st.metric("Scheduled Events", "12")
    st.metric("Expected Visitors", "430")
    st.metric("Surface Coverage", "92% booked")

    st.markdown("### Forecasted Traffic (Next 3 Days)")
    st.write("📅 Tomorrow (Friday): 14 events, 520 guests")
    st.write("📅 Saturday: 22 events, 860 guests")
    st.write("📅 Sunday: 18 events, 690 guests")

    st.markdown("### Alerts")
    st.warning("🏀 Court 2 double-booked Sat 12–2pm — review schedule")
    st.success("☀️ Sunday weather looks clear — confirm all outdoor sessions")
    st.info("⚽ Consider promoting morning turf availability for youth games")
