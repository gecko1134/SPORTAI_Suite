
import streamlit as st

def run():
    st.title("🎯 Donation Campaign Tracker")

    goal = 250000
    current = 184750
    percent = current / goal

    st.markdown("### Turf + Trail Expansion Fund")
    st.progress(percent)
    st.metric("Raised So Far", f"${current:,}")
    st.metric("Goal", f"${goal:,}")

    st.markdown("### What This Funds")
    st.markdown("- 🏞️ New community trail overlays")
    st.markdown("- 🧍 Adaptive program turf conversion")
    st.markdown("- 🏆 Dome scoreboard & seating expansion")

    st.success("Thank you to over 180 donors so far!")
