import streamlit as st
import pandas as pd

def run():
    st.title("👥 Membership CRM Tracker")

    df = pd.DataFrame({
        "Member": ["Jordan", "Casey", "Dana"],
        "Tier": ["Elite", "Silver", "Family"],
        "Join Date": ["2023-06-01", "2024-01-15", "2023-10-10"],
        "Expires": ["2024-06-01", "2025-01-15", "2024-10-10"],
        "Credits Remaining": [12, 4, 20],
        "Usage Hours": [38, 10, 22]
    })
    df["Upgrade Flag"] = df["Credits Remaining"].apply(lambda x: "Yes" if x < 5 else "No")
    st.dataframe(df)