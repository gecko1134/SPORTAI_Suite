import streamlit as st
import pandas as pd

def run():
    st.title("📋 Active Sponsorship Tracker")

    sponsors = pd.DataFrame({
        "Sponsor": ["Nike", "BankCo", "Health Group"],
        "Asset": ["Court 1", "Dome Exterior", "Turf A + Scoreboard"],
        "Start Date": ["2024-01-01", "2024-04-15", "2023-11-01"],
        "End Date": ["2025-01-01", "2024-10-15", "2024-11-01"],
        "Tier": ["Platinum", "Gold", "Silver"],
        "Value ($)": [50000, 30000, 15000]
    })

    st.dataframe(sponsors)
    st.download_button("📥 Export Tracker", sponsors.to_csv(index=False), "sponsor_tracker.csv")