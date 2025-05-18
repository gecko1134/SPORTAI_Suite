
import streamlit as st
import pandas as pd

def run():
    st.title("🧍 Referee & Volunteer Tracker")

    df = pd.DataFrame({
        "Name": ["Alex J.", "Sam T.", "Dana K."],
        "Role": ["Referee", "Volunteer", "Referee"],
        "Cert Status": ["Valid", "Pending", "Expired"],
        "Shifts This Week": [3, 2, 1]
    })
    st.dataframe(df)
    st.success("Alex J. cleared for next 3 game slots.")
