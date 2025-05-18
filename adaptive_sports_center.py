
import streamlit as st
import pandas as pd

def run():
    st.title("♿ Adaptive Sports Center")

    df = pd.DataFrame({
        "Program": ["Wheelchair Basketball", "Seated Volleyball", "Power Soccer"],
        "Age Group": ["Youth", "Adult", "Youth/Adult"],
        "Court Need": ["Court 1", "Court 2", "Turf"],
        "Equipment": ["Chairs", "Low net", "Power chairs + ball guard"],
        "Staff Cert Required": ["Yes", "No", "Yes"]
    })
    st.dataframe(df)

    st.markdown("### Accessibility Notes")
    st.success("All sports require accessible entry route, bench-free sidelines, and staff trained in adaptive safety.")
