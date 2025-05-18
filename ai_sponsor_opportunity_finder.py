
import streamlit as st
import pandas as pd

def run():
    st.title("📈 AI Sponsor Opportunity Finder")

    st.markdown("### Unfilled Assets")
    assets = pd.DataFrame({
        "Asset": ["Court 3", "Half Turf", "Scoreboard 2", "Pavilion Banner"],
        "Status": ["Unfilled", "Unfilled", "Expiring Soon", "Unfilled"],
        "Last Sponsored": ["-", "-", "BankCo", "-"],
        "Exposure": ["High", "Moderate", "High", "Moderate"]
    })
    st.dataframe(assets)

    st.markdown("### Suggested Matches")
    st.info("🏥 Health Systems → Half Turf (clinic partnership)")
    st.info("🏦 Local Credit Union → Scoreboard 2 (family visibility)")
    st.info("🥤 Energy Drink Co → Court 3 + event booth bundle")

    st.success("3 unfilled assets flagged for activation.")
    st.warning("Scoreboard 2 expiring in 14 days – recommend renewal pitch.")
