
import streamlit as st
import pandas as pd

def run():
    st.title("🌍 International Team Portal")

    df = pd.DataFrame({
        "Team Name": ["Berlin FC", "Tokyo Juniors", "Madrid Elite"],
        "Country": ["Germany", "Japan", "Spain"],
        "Sport": ["Soccer", "Basketball", "Volleyball"],
        "Arrival": ["2024-08-02", "2024-09-10", "2024-10-01"],
        "Matches Requested": [3, 2, 4]
    })
    st.dataframe(df)

    st.markdown("### Hosting Notes")
    st.info("🛏️ Lodging + translation requested for Tokyo Juniors.")
    st.success("🤝 Madrid Elite matched with local exchange school program.")
    st.warning("📅 Ensure match slots don’t conflict with regional leagues.")
