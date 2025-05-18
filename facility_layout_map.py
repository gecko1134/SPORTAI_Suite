
import streamlit as st
import pandas as pd

def run():
    st.title("🗺️ Facility Layout Map")

    st.markdown("### Surface Booking Overview")

    df = pd.DataFrame({
        "Surface": ["Court 1", "Court 2", "Court 3", "Court 4", "Full Turf", "Half Turf"],
        "Status": ["Booked", "Available", "Booked", "Available", "Booked", "Underused"],
        "Sport": ["Basketball", "-", "Volleyball", "-", "Soccer", "Flag Football"],
        "Booked Hours": [6, 0, 4, 0, 7, 2],
        "Max Hours": [8, 8, 8, 8, 10, 6]
    })
    df["Utilization %"] = (df["Booked Hours"] / df["Max Hours"] * 100).round(1)

    st.dataframe(df)

    st.markdown("### Smart Visuals")
    st.warning("⚠️ Half Turf only 33% booked today.")
    st.success("✅ Full Turf usage at 90%. Maintain pricing.")
    st.info("🔄 Court 2 idle — suggest rec league filler.")
