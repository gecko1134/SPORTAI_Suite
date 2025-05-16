import streamlit as st
import pandas as pd

def run():
    st.title("🧭 Event Control Panel")

    st.markdown("### View or Edit Events (All Types)")
    df = pd.DataFrame({
        "Event": ["Youth Soccer", "Wedding Expo", "Movie Night", "Esports Finals"],
        "Type": ["Sport", "Non-Sport", "Non-Sport", "Non-Sport"],
        "Surface": ["Turf A", "Pavilion", "Court 2", "Court 1"],
        "Start": ["2024-07-01 10:00", "2024-07-02 15:00", "2024-07-04 20:00", "2024-07-06 13:00"],
        "Hours": [2, 5, 3, 6],
        "Status": ["Booked", "Booked", "Booked", "Setup"]
    })

    st.dataframe(df)
    st.info("🧠 AI Alert: Movie Night overlaps with cleaning buffer — reschedule 30 mins later.")