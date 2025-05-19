
import streamlit as st
import pandas as pd

def run():
    st.title("🔁 Grant Renewal Tracker")

    df = pd.DataFrame({
        "Grant Name": ["Play60 Foundation", "Green Rec Fund", "Tourism Grant"],
        "Approved On": ["2023-08-01", "2024-01-15", "2023-10-10"],
        "Next Reapply": ["2024-08-01", "2025-01-15", "2024-10-10"],
        "Required Docs": ["Report + Budget", "Impact Narrative", "Photos + ROI Chart"],
        "Status": ["Prep", "Scheduled", "Prep"]
    })

    st.dataframe(df)
    st.warning("⏰ Play60 reapply due in <60 days.")
    st.success("✅ Green Rec scheduled for Q1 2025.")

    st.markdown("👉 Use AI Grant Writer to pre-fill narrative for your renewal.")
