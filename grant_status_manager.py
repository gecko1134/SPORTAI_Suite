
import streamlit as st
import pandas as pd

def run():
    st.title("📋 Grant Status Tracker")

    df = pd.DataFrame({
        "Grant Name": ["Play60 Foundation", "Green Rec Fund", "Tourism Grant"],
        "Category": ["Youth Sports", "Trails", "Tourism"],
        "Status": ["Submitted", "Approved", "Draft"],
        "Amount ($)": [10000, 15000, 25000],
        "Due Date": ["2024-06-30", "-", "2024-07-15"]
    })

    st.dataframe(df)
    st.warning("⏳ Tourism Grant due July 15 – finalize submission.")
    st.success("💵 Green Rec Fund approved – integrate into pro forma.")
