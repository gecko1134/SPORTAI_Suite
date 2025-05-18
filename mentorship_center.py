
import streamlit as st
import pandas as pd

def run():
    st.title("🧑‍🏫 Mentorship Center")

    df = pd.DataFrame({
        "Mentor": ["Coach A", "Director B", "Board Member C"],
        "Mentee": ["Athlete 1", "Student 2", "Captain 3"],
        "Focus": ["Leadership", "Career Path", "Sports Management"],
        "Last Session": ["2024-05-01", "2024-04-18", "2024-04-30"]
    })
    st.dataframe(df)

    st.success("Next mentorship sync scheduled for 2024-06-10.")
