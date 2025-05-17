import streamlit as st
import pandas as pd

def run():
    st.title("📊 Complex Usage Optimizer")

    st.markdown("### Current Court/Turf Assignments")
    df = pd.DataFrame({
        "Surface": ["Court 1", "Court 2", "Court 3", "Court 4", "Full Turf", "Half Turf"],
        "Sport": ["Basketball", "Pickleball", "Volleyball", "Basketball", "Soccer", "Flag Football"],
        "Hours Booked": [32, 24, 30, 36, 40, 28],
        "Total Available": [40, 40, 40, 40, 50, 30]
    })
    df["Utilization %"] = (df["Hours Booked"] / df["Total Available"] * 100).round(1)
    st.dataframe(df)

    st.markdown("### AI Layout Suggestion")
    st.info("🏀 Court 3 overbooked → suggest converting Court 2 to flex Volleyball/Basketball layout.")
    st.success("⚽ Turf usage at 80% — consider expanding Half Turf hours to off-peak weekends.")
    st.warning("🏐 Pickleball under 60% usage — offer club package discount.")