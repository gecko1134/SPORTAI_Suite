
import streamlit as st
import pandas as pd

def run():
    st.title("👥 Team & Club Manager")
    df = pd.DataFrame({
        "Team": ["Raiders", "Storm Elite", "ThunderCats"],
        "Sport": ["Flag Football", "Basketball", "Soccer"],
        "Division": ["12U", "Varsity", "14U"],
        "Coach": ["Coach A", "Coach B", "Coach C"]
    })
    st.dataframe(df)
    st.success("Storm Elite has confirmed 5 bookings this season.")
