
import streamlit as st
import pandas as pd

def run():
    st.title("👥 Governance Admin")

    df = pd.DataFrame({
        "Name": ["Jordan Smith", "Taylor Kim", "Dana Lopez", "Coach B"],
        "Role": ["Board Chair", "Liaison", "Booster Club Lead", "Nonprofit Treasurer"],
        "Type": ["Board", "Liaison", "Booster", "Finance"]
    })
    st.dataframe(df)
    st.success("View, assign, or update roles across for-profit/nonprofit structure.")
