
import streamlit as st
import pandas as pd

def run():
    st.title("🔐 Sponsorship Inventory Control")

    df = pd.DataFrame({
        "Asset": ["Court 1", "Court 2", "Full Turf", "Half Turf", "Scoreboard", "Wall Banner Zone A"],
        "Max Sponsors": [1, 1, 1, 1, 1, 3],
        "Current Sponsors": [1, 0, 1, 1, 1, 2],
        "Available": [0, 1, 0, 0, 0, 1]
    })

    st.dataframe(df)
    st.warning("⚠️ All naming slots filled — lock to prevent overbooking")
    st.success("✅ Wall Banner Zone A has 1 slot available")
