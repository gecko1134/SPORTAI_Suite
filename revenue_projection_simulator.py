
import streamlit as st

def run():
    st.title("📈 Revenue Projection Simulator")

    st.markdown("### Input Assumptions")
    court_hours = st.number_input("Court Rentals per Month", 0, 1000, 240)
    court_rate = st.number_input("Court Rate ($/hr)", 0, 200, 75)
    turf_hours = st.number_input("Turf Rentals per Month", 0, 1000, 180)
    turf_rate = st.number_input("Turf Rate ($/hr)", 0, 300, 125)

    sponsor_income = st.number_input("Monthly Sponsorship Income", 0, 50000, 12000)
    event_revenue = st.number_input("Avg Monthly Event Revenue", 0, 50000, 18000)
    expenses = st.number_input("Monthly Expenses (staff/utilities/ops)", 0, 50000, 22000)

    total_rev = (court_hours * court_rate) + (turf_hours * turf_rate) + sponsor_income + event_revenue
    net = total_rev - expenses

    st.metric("Total Monthly Revenue", f"${total_rev:,.0f}")
    st.metric("Estimated Net", f"${net:,.0f}", delta="Profit" if net >= 0 else "Loss")
    st.success("✅ Use this tool to model projections for board or grant funding.")
