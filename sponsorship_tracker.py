
import streamlit as st
import pandas as pd
from datetime import datetime

def run():
    st.title("📋 Sponsorship Tracker + Smart Alerts")

    df = pd.DataFrame({
        "Sponsor": ["Nike", "BankCo", "Orthopedic Group", "TechNow"],
        "Asset": ["Court 1", "Scoreboard", "Turf", "Digital Banner"],
        "Start": ["2023-06-01", "2024-03-01", "2023-10-15", "2024-01-10"],
        "End": ["2024-06-01", "2024-09-01", "2024-10-15", "2025-01-10"],
        "Tier": ["Gold", "Silver", "Platinum", "Bronze"]
    })

    df["End"] = pd.to_datetime(df["End"])
    today = pd.to_datetime("today")
    df["Status"] = df["End"].apply(lambda x: "✅ Active" if x > today else "🛑 Expired")
    df.loc[(df["End"] - today).dt.days < 30, "Status"] = "⚠️ Renew Soon"

    st.dataframe(df)

    st.markdown("### Insights")
    expiring = df[df["Status"] == "⚠️ Renew Soon"]
    if not expiring.empty:
        st.warning(f"{len(expiring)} contracts expiring soon. Prioritize renewals:")
        for _, row in expiring.iterrows():
            st.markdown(f"- {row['Sponsor']} on {row['Asset']} (ends {row['End'].date()})")
    else:
        st.success("No contracts within 30-day expiration.")
