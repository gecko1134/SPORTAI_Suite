
import streamlit as st

def run():
    st.title("🚦 Facility Capacity & Load Alerts")

    st.markdown("### Today’s Fill Rate")
    st.metric("Overall Capacity", "78%", delta="↑ 4% from last week")

    st.markdown("### Surface Breakdown")
    st.progress(0.90)
    st.write("Full Turf: 90% booked")

    st.progress(0.55)
    st.write("Court 2: 55% booked – consider flash rental")

    st.progress(0.35)
    st.write("Court 4: 35% booked – alert ops team")

    st.markdown("### AI Observations")
    st.warning("⚠️ Court 4 bookings <40% for 3 straight days – trend detected")
    st.info("📢 Consider pairing underused slots with youth programs or drop-ins")
    st.success("📈 Full Turf running at optimal load – maintain current rate")
