
import streamlit as st
import pandas as pd

def run():
    st.title("🔐 Member Access Log")

    st.markdown("Example access log from QR/fob check-ins")
    df = pd.DataFrame({
        "Member": ["Jordan", "Taylor", "Casey", "Jordan"],
        "Time": ["8:00 AM", "9:15 AM", "10:45 AM", "12:00 PM"],
        "Surface": ["Court 1", "Turf", "Court 2", "Court 3"]
    })
    st.dataframe(df)
    st.download_button("Download Log", df.to_csv(index=False), "access_log.csv")
