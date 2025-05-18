
import streamlit as st
import pandas as pd

def run():
    st.title("📊 Sponsor Dashboard")

    df = pd.DataFrame({
        "Sponsor": ["Nike", "BankCo", "Health Systems"],
        "Asset Sponsored": ["Court 1", "Scoreboard", "Turf"],
        "Start Date": ["2024-01-01", "2024-03-15", "2024-02-20"],
        "End Date": ["2025-01-01", "2024-09-15", "2024-12-20"],
        "Tier": ["Gold", "Silver", "Platinum"]
    })
    st.dataframe(df)
    st.info("Next renewal: BankCo – 2024-09-15")
