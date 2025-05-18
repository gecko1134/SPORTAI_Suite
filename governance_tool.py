
import streamlit as st
import pandas as pd

def run():
    st.title("🧭 Governance Dashboard")
    st.markdown("View current board members, roles, and voting access.")
    df = pd.DataFrame({
        "Name": ["Jordan Smith", "Dana Lopez", "Taylor Kim"],
        "Role": ["Chair", "Treasurer", "Secretary"],
        "Voting Rights": ["Yes", "Yes", "Yes"]
    })
    st.dataframe(df)
    st.success("Next board meeting scheduled for: 2024-08-15")
