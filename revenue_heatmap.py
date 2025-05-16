
import streamlit as st
import pandas as pd

def run():
    st.title("💵 Revenue Heatmap (Courts + Turf)")

    data = pd.DataFrame({
        "Hour": ["8am", "9am", "10am", "11am", "12pm"],
        "Court 1": [80, 100, 90, 120, 85],
        "Court 2": [75, 95, 85, 110, 70],
        "Court 3": [70, 90, 100, 105, 80],
        "Court 4": [65, 85, 95, 100, 60],
        "Full Turf": [300, 320, 310, 330, 290],
        "Half Turf": [160, 150, 180, 200, 170]
    })
    st.dataframe(data)
    st.bar_chart(data.set_index("Hour"))
