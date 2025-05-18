
import streamlit as st
import pandas as pd

def run():
    st.title("📅 Event Admin Panel")

    df = pd.DataFrame({
        "Event": ["Youth Soccer Tourney", "Wedding Rental", "Volleyball Classic"],
        "Date": ["2024-08-10", "2024-09-01", "2024-07-20"],
        "Surface": ["Full Turf", "Full Dome", "Court 1-3"],
        "Contact": ["Jordan", "Alex", "Dana"]
    })
    st.dataframe(df)
    st.warning("🔧 Future enhancement: edit/delete buttons & export")
