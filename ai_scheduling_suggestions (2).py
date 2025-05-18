
import streamlit as st
import pandas as pd

def run():
    st.title("📅 AI Scheduling Suggestions")

    st.markdown("### Detected Gaps + Optimization")

    data = pd.DataFrame({
        "Surface": ["Court 1", "Court 2", "Turf A", "Court 3"],
        "Gap Start": ["1:00 PM", "11:00 AM", "2:30 PM", "10:00 AM"],
        "Gap End": ["3:00 PM", "1:00 PM", "4:30 PM", "12:00 PM"],
        "Suggested Use": [
            "Drop-in rec basketball",
            "Local youth clinic",
            "Sponsor demo or training",
            "Pickleball social league"
        ]
    })
    st.dataframe(data)

    st.markdown("### AI Recommendations")
    st.success("Court 2 open 11–1pm → Recommend youth 2-hr pop-up clinic.")
    st.warning("Turf A available 2:30–4:30pm → Offer low-rate private rental.")
    st.info("Court 1 gap detected 1–3pm → Suggest rec league backfill.")
