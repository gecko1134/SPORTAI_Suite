
import streamlit as st

def run():
    st.title("🗺️ Sponsored Asset Map")

    st.markdown("View which surfaces or zones are sponsored.")

    assets = {
        "Court 1": "Nike (Gold)",
        "Court 2": "Available",
        "Court 3": "HealthCo (Silver)",
        "Court 4": "BankCo (Bronze)",
        "Full Turf": "Open",
        "Half Turf": "TechNow (Platinum)",
        "Scoreboard": "BankCo (Silver)"
    }

    for surface, sponsor in assets.items():
        status = "✅ Sponsored" if sponsor != "Available" and sponsor != "Open" else "❌ Available"
        st.markdown(f"**{surface}** → {sponsor} | {status}")
