
import streamlit as st
import pandas as pd

def run():
    st.title("📅 Public Schedule Viewer")

    st.markdown("View upcoming bookings and events. This is a read-only viewer for public access.")

    df = pd.DataFrame({
        "Date": ["2024-06-12", "2024-06-12", "2024-06-13", "2024-06-14"],
        "Time": ["10:00 AM", "2:00 PM", "9:00 AM", "6:00 PM"],
        "Surface": ["Court 1", "Full Turf", "Court 2", "Half Turf"],
        "Event": ["Youth Basketball Practice", "Flag Football", "Rec Volleyball", "Archery Expo"]
    })

    st.dataframe(df)
    st.info("📢 Note: Public events are view-only. Contact admin for booking access.")
