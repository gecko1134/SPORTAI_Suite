
import streamlit as st
import pandas as pd

def run():
    st.title("👤 Donor Profile Creator")

    name = st.text_input("Donor Name")
    donor_type = st.selectbox("Donor Type", ["Individual", "Business", "Foundation", "Alumni"])
    amount = st.number_input("Donation Amount ($)", 100, 100000, 1000)
    category = st.selectbox("Funding Area", ["Youth Sports", "Adaptive Programs", "Facility Upgrade", "Scholarships", "Equipment"])

    if st.button("Save Donor"):
        st.success(f"Saved: {name} - ${amount:,} to {category} ({donor_type})")

    st.markdown("📝 Use this to build donor logs and trigger follow-up messaging.")
