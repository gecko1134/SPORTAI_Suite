
import streamlit as st
import pandas as pd

def run():
    st.title("🙋 Volunteer Hub")

    df = pd.DataFrame({
        "Name": ["Dana K.", "Jordan S.", "Chris P."],
        "Hours Logged": [12, 8, 16],
        "Badge Level": ["Bronze", "Bronze", "Silver"]
    })
    st.dataframe(df)
    st.success("Chris P. eligible for event entry pass.")
