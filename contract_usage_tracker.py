import streamlit as st
import pandas as pd

def run():
    st.title("📑 Contract Tracker")
    data = pd.DataFrame({
        "Organization": ["UMD", "ACME Inc"],
        "Purchased": [100, 200],
        "Used": [80, 120]
    })
    data["Remaining"] = data["Purchased"] - data["Used"]
    st.dataframe(data)