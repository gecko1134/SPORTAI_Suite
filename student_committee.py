
import streamlit as st
import pandas as pd

def run():
    st.title("🎓 Student Committee Tracker")
    df = pd.DataFrame({
        "Name": ["Alex J.", "Sam T.", "Jordan K."],
        "School": ["West HS", "North HS", "Central HS"],
        "Sport Rep": ["Basketball", "Soccer", "Volleyball"],
        "Status": ["Active", "Pending", "Active"]
    })
    st.dataframe(df)
    st.info("Next student summit: Aug 12, 2024")
