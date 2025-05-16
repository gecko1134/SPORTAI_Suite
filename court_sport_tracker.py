
import streamlit as st
import pandas as pd

def run():
    st.title("🏟️ Sport Assignment Tracker")

    st.markdown("Log what sport is being played on each surface.")
    surface = st.selectbox("Surface", ["Court 1", "Court 2", "Court 3", "Court 4", "Full Turf", "Half Turf"])
    sport = st.text_input("Sport")
    team = st.text_input("Team or Age Group")
    time = st.time_input("Time Block")
    if st.button("Log Assignment"):
        st.success(f"{sport} logged on {surface} for {team} at {time}.")
