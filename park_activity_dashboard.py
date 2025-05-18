
import streamlit as st

def run():
    st.title("🌐 Park Activity Dashboard")

    st.subheader("Dome")
    st.info("🎯 14 active bookings today — 82% full")
    st.success("⚽ Full Turf used for 3 team practices")
    st.warning("Court 2 has no scheduled events from 11am–2pm")

    st.subheader("Outdoor Trails")
    st.metric("Bike Trail Traffic", "Moderate")
    st.metric("Hike Path Status", "Good")
    st.metric("Snowmobile Loop", "Clear")
    st.warning("⚠️ ATV Trail wet in areas")

    st.subheader("Pavilions & Events")
    st.info("🎪 Expo Pavilion reserved Sat 8am–5pm")
    st.success("🥤 Sponsor booth setup confirmed")
