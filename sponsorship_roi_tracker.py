
import streamlit as st

def run():
    st.title("📈 Sponsorship ROI Tracker")

    st.markdown("Estimate return on investment for each sponsor.")
    st.metric("Nike ROI", "215%")
    st.metric("BankCo ROI", "185%")
    st.success("Most effective asset: Scoreboard + Court Bundle")
