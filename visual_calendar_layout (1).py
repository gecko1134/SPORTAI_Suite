
import streamlit as st
import pandas as pd

def run():
    st.title("📅 Visual Calendar Layout")

    st.markdown("Hover-based layout of surface assignments (example view):")
    df = pd.DataFrame({
        "Hour": ["8am", "9am", "10am", "11am"],
        "Court 1": ["Basketball", "Basketball", "Open", "Volleyball"],
        "Court 2": ["Open", "Pickleball", "Open", "Open"],
        "Full Turf": ["Soccer", "Open", "Flag Football", "Soccer"]
    })
    st.dataframe(df)
