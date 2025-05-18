
import streamlit as st

def run():
    st.title("🏆 League Coordinator")

    st.markdown("Track leagues, age groups, divisions, and game days.")
    sport = st.selectbox("Sport", ["Basketball", "Soccer", "Volleyball", "Flag Football"])
    division = st.text_input("Division or Age Group")
    next_game = st.date_input("Next Scheduled Game")
    if st.button("Add League Entry"):
        st.success(f"{sport} league ({division}) scheduled for {next_game}.")
