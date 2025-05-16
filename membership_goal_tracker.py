import streamlit as st
import pandas as pd

def run():
    st.title("🎯 Membership Growth Goals")

    goals = pd.DataFrame({
        "Tier": ["Basic", "Silver", "Elite", "Family"],
        "Current": [112, 86, 42, 29],
        "Target": [150, 100, 60, 40]
    })
    goals["Progress"] = (goals["Current"] / goals["Target"] * 100).round(1).astype(str) + "%"
    st.dataframe(goals)
    st.metric("Total Members", sum(goals["Current"]))