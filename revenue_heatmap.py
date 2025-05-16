import streamlit as st
import pandas as pd

def run():
    st.title("💵 Revenue Heatmap")
    df = pd.DataFrame({
        "Hour": ["8-9", "9-10", "10-11"],
        "Court 1": [80, 120, 60],
        "Court 2": [90, 100, 40],
        "Turf": [300, 450, 200]
    })
    st.dataframe(df)
    st.line_chart(df.set_index("Hour"))