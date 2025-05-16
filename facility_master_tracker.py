import streamlit as st
import pandas as pd

def run():
    st.title("📊 Facility Master Tracker")

    st.markdown("### Dome + Park Revenue Overview")
    df = pd.DataFrame({
        "Category": ["Sponsorships", "Memberships", "Events", "Rentals", "Food"],
        "Monthly ($)": [60000, 15000, 8000, 12000, 4000]
    })
    df["YTD ($)"] = df["Monthly ($)"] * 5
    st.dataframe(df)
    st.metric("Total YTD Revenue", f"${df['YTD ($)'].sum():,.0f}")