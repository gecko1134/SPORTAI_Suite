
import streamlit as st

def run():
    st.title("💰 AI Revenue Maximizer")

    st.markdown("### Price Optimization Tool")
    surface = st.selectbox("Select Surface", ["Court 1", "Court 2", "Court 3", "Court 4", "Full Turf", "Half Turf"])
    base_rate = st.slider("Current Hourly Rate ($)", 30, 200, 75)
    demand_level = st.selectbox("Demand Level", ["Low", "Moderate", "High"])

    multiplier = {"Low": 0.8, "Moderate": 1.0, "High": 1.3}[demand_level]
    suggested_rate = round(base_rate * multiplier, 2)

    st.metric("Suggested Dynamic Rate", f"${suggested_rate}")
    st.info("Apply dynamic pricing to high-demand hours or bundle with advertising assets.")

    st.markdown("### Yield Insights")
    st.success("⚽ Full Turf usage 90% at $100/hr — hold rate")
    st.warning("🏀 Court 2 only 55% booked at $75/hr — consider drop to $60 or bundle with scoreboard")
    st.info("📅 Friday 3–5pm is underbooked across surfaces — test group discount or event insert")
