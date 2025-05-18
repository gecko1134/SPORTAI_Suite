
import streamlit as st
import pandas as pd

def run():
    st.title("📊 Surface Demand Heatmap")

    df = pd.DataFrame({
        "Surface": ["Court 1", "Court 2", "Court 3", "Court 4", "Full Turf", "Half Turf", "Bike Trail", "Hike Trail"],
        "Avg Weekly Usage (hrs)": [38, 22, 34, 18, 45, 28, 12, 14],
        "Peak Season": ["Winter", "Spring", "Fall", "Summer", "Spring", "Fall", "Summer", "Fall"]
    })

    st.dataframe(df)
    st.markdown("### AI Insight")
    st.warning("Court 4 under 50% capacity – consider bundle promotion.")
    st.info("Bike trail underused in Spring – schedule guided ride.")
