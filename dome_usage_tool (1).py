
import streamlit as st
import pandas as pd

def run():
    st.title("🏟️ Dome Usage Tracker")

    data = pd.DataFrame({
        "Hour": ["8am", "9am", "10am", "11am", "12pm"],
        "Court 1": ["Basketball", "Basketball", "Open", "Volleyball", "Open"],
        "Court 2": ["Open", "Pickleball", "Open", "Open", "Basketball"],
        "Court 3": ["Open", "Volleyball", "Open", "Open", "Open"],
        "Court 4": ["Basketball", "Open", "Basketball", "Open", "Open"],
        "Full Turf": ["Soccer", "Open", "Flag Football", "Soccer", "Soccer"],
        "Half Turf": ["Open", "Open", "Soccer", "Flag Football", "Open"]
    })
    st.dataframe(data)
    st.success("Track current bookings and optimize future availability.")
