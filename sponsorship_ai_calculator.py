
import streamlit as st

def run():
    st.title("💼 Sponsorship AI Calculator")
    st.markdown("### Select Sponsorship Assets")

    assets = {
        "Full Dome Naming": 50000,
        "Court 1": 5000,
        "Court 2": 5000,
        "Court 3": 5000,
        "Court 4": 5000,
        "Full Turf": 10000,
        "Half Turf": 6000,
        "Scoreboard": 4000,
        "Banners": 2000,
        "Digital Ads": 1500
    }

    selected = st.multiselect("Available Assets", list(assets.keys()))
    total = sum([assets[k] for k in selected])

    tier = "Platinum" if total > 30000 else "Gold" if total > 15000 else "Silver" if total > 5000 else "Bronze"

    st.metric("Estimated Value", f"${total:,.0f}")
    st.success(f"Suggested Tier: {tier}")
