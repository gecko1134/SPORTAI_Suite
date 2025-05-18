
import streamlit as st
import pandas as pd

def run():
    st.title("🎓 Scholarship Tracker")

    st.markdown("Track awarded scholarships and recipients.")
    df = pd.DataFrame({
        "Recipient": ["Alex Johnson", "Taylor Kim", "Jamie Rios"],
        "Type": ["Athletic", "Academic", "Leadership"],
        "Amount": [1000, 1500, 1200],
        "Status": ["Awarded", "Pending", "Awarded"]
    })
    st.dataframe(df)
    st.success("Total Awarded: $2,200")
