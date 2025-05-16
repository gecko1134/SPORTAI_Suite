import streamlit as st
import pandas as pd

def run():
    st.title("🎓 Scholarship Fund Manager")

    category = st.selectbox("Scholarship Type", [
        "Sport Performance", "Academic Merit", "Volunteer Referee Grant", "Coach Training", "Event-Based Award"
    ])
    sponsor = st.text_input("Sponsored By (optional)")
    amount = st.slider("Amount ($)", 100, 10000, 1000, step=100)
    renewable = st.radio("Renewable?", ["Yes", "No"])
    recipients = st.number_input("Expected Recipients", min_value=1, value=1)

    if st.button("Log Scholarship"):
        st.success(f"{category} scholarship of ${amount:,} logged for {recipients} recipient(s).")