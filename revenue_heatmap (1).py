
import streamlit as st
import pandas as pd

def run():
    st.title("💵 Revenue Heatmap + Usage Insights")

    st.markdown("### Hourly Surface Revenue (Today)")

    df = pd.DataFrame({
        "Hour": ["8am", "9am", "10am", "11am", "12pm"],
        "Court 1": [60, 90, 100, 75, 60],
        "Court 2": [70, 80, 85, 90, 75],
        "Court 3": [65, 70, 95, 100, 60],
        "Court 4": [80, 85, 60, 70, 55],
        "Full Turf": [200, 240, 210, 230, 190],
        "Half Turf": [120, 110, 140, 160, 130]
    })

    st.dataframe(df)
    st.line_chart(df.set_index("Hour"))

    st.markdown("### Smart Suggestions")
    st.warning("📉 Court 4 dropped to $55/hr at noon – suggest discount rental push.")
    st.info("⚽ Full Turf revenue steady – maintain soccer block promotion.")
    st.success("📈 Half Turf climbed 140 → 160 → promote combo with Court 2.")
