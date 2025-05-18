
import streamlit as st

def run():
    st.title("📋 Facility Contract Monitor")
    st.markdown("Overview of contracts by facility type and surface.")
    st.info("Court 1 contract with UMD: 85% used – expires 12/31/24.")
    st.warning("Turf B contract with ClubX: only 35% used – suggest renegotiation or discount extension.")
    st.success("Scoreboard ad contract with BankCo renewed for 2025.")
