import streamlit as st

def run():
    st.title("🗂️ Sponsorship Availability Overview")

    assets = {
        "Court 1": "Taken",
        "Court 2": "Available",
        "Turf A": "Taken",
        "Turf B": "Available",
        "Scoreboard": "Taken",
        "Dome Exterior": "Taken",
        "Light Poles": "Available",
        "Pavilion": "Available"
    }

    for asset, status in assets.items():
        if status == "Taken":
            st.warning(f"{asset} – TAKEN")
        else:
            st.success(f"{asset} – AVAILABLE")

    st.markdown("💡 Bundle Turf B + Court 2 for a mid-tier sponsor.")