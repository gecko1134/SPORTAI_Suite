
import streamlit as st
import time

def run():
    st.set_page_config(page_title="Sponsor Display", layout="wide")
    st.title("🎥 Venture North Digital Display")

    st.markdown("### Today’s Events")
    st.markdown("- 9:00 AM – Youth Basketball (Court 1)")
    st.markdown("- 10:30 AM – Pickleball Open (Court 3)")
    st.markdown("- 12:00 PM – Flag Football (Full Turf)")
    st.markdown("- 2:00 PM – Archery Expo Setup")

    st.markdown("### Thank You to Our Sponsors:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("🏆 TechNow – Half Turf Sponsor")
    with col2:
        st.info("🏅 BankCo – Scoreboard")
    with col3:
        st.warning("🎯 Nike – Court 1 Naming")

    st.markdown("### Facility Status")
    st.metric("Court Utilization", "85%")
    st.metric("Turf Booked", "92%")
    st.caption("Auto-refreshes every 60 seconds")

    time.sleep(60)
