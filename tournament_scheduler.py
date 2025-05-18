
import streamlit as st
import pandas as pd

def run():
    st.title("🏆 Tournament Scheduler")

    st.markdown("### Build and Track Multi-Team Events")
    sport = st.selectbox("Sport", ["Soccer", "Basketball", "Volleyball", "Lacrosse", "Softball", "Flag Football"])
    level = st.selectbox("Level", ["Youth", "HS", "College", "Semi-Pro", "Pro", "International"])
    teams = st.number_input("Number of Teams", min_value=4, max_value=64, value=8, step=2)
    days = st.slider("Days", 1, 5, 2)

    st.success(f"{teams}-team {level} {sport} tournament booked for {days} days.")
    st.info("Use the Facility Layout tool to auto-assign rounds to surfaces.")
    st.warning("Don’t forget to schedule referees, scorekeepers, and sponsorship overlays.")
