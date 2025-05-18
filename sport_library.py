
import streamlit as st
import pandas as pd

def run():
    st.title("🏟️ Dome Sport Library")

    df = pd.DataFrame({
        "Sport": [
            "Soccer", "Lacrosse", "Volleyball", "Softball", "Baseball",
            "Floor Hockey", "Flag Football", "Disc Golf", "Golf", "Track", "CrossFit"
        ],
        "Default Surface": [
            "Full Turf", "Full Turf", "Court", "Half Turf", "Half Turf",
            "Court", "Half Turf", "Turf", "Turf", "Court", "Turf"
        ],
        "Typical Duration": ["1 hr"]*11,
        "Season": ["Year-Round", "Spring", "Winter", "Spring", "Spring", "Winter", "Fall", "Summer", "Year-Round", "Winter", "Year-Round"]
    })
    st.dataframe(df)
