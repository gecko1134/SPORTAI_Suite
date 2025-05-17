import streamlit as st
import pandas as pd

def run():
    st.title("🏟️ Dome Usage Tool")

    st.markdown("### Daily Court and Turf Usage Tracker")
    data = pd.DataFrame({
        "Time": ["8am", "9am", "10am", "11am", "12pm"],
        "Court 1": ["Basketball", "Basketball", "Open", "Volleyball", "Open"],
        "Court 2": ["Open", "Pickleball", "Pickleball", "Open", "Basketball"],
        "Court 3": ["Volleyball", "Volleyball", "Basketball", "Open", "Open"],
        "Court 4": ["Open", "Open", "Basketball", "Basketball", "Open"],
        "Full Turf": ["Soccer", "Soccer", "Flag Football", "Open", "Soccer"],
        "Half Turf": ["Open", "Soccer", "Open", "Flag Football", "Open"]
    })

    st.dataframe(data)
    st.markdown("🔄 Use this to review dome booking patterns and identify underused time slots.")
    st.info("Suggestion: Offer promo rentals for Half Turf between 11am–1pm.")