
import streamlit as st

def run():
    st.title("💼 Sponsorship Revenue Builder")

    asset = st.selectbox("Sponsorship Asset", ["Court 1", "Turf", "Scoreboard", "Banner", "Naming Rights"])
    tier = st.selectbox("Tier", ["Bronze", "Silver", "Gold", "Platinum"])
    duration = st.slider("Duration (months)", 1, 36, 12)
    base_value = st.number_input("Base Monthly Value ($)", 500, 20000, 1500)

    total_value = base_value * duration
    st.metric("Projected Sponsorship Total", f"${total_value:,.0f}")
    st.info(f"{tier} tier on {asset} over {duration} months")
