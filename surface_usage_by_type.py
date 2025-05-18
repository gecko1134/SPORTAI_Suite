
import streamlit as st
import pandas as pd

def run():
    st.title("🧠 Surface Usage by Booking Type")

    df = pd.DataFrame({
        "Surface": ["Court 1", "Court 2", "Full Turf", "Half Turf"],
        "Individual (hrs)": [12, 8, 5, 4],
        "Group (hrs)": [16, 20, 12, 14],
        "Team (hrs)": [30, 28, 40, 26],
        "Tournament (hrs)": [8, 12, 30, 10],
        "Scrimmage (hrs)": [6, 5, 10, 8]
    })
    df["Total"] = df.sum(axis=1, numeric_only=True)
    st.dataframe(df)
