
import streamlit as st
from datetime import datetime

def run():
    st.title("🕒 Screen Rotation Scheduler")

    st.markdown("Set time-based display schedules for digital screens.")

    now = datetime.now().strftime("%H:%M")
    st.info(f"🕑 Current time: {now}")

    display_window = st.slider("Display Schedule", 6, 24, (8, 22))
    screen_mode = st.selectbox("Screen Content", ["Sponsor Wall", "Event Feed", "Court Map", "Promo Loop"])

    st.success(f"✅ {screen_mode} scheduled from {display_window[0]}:00 to {display_window[1]}:00 daily.")
