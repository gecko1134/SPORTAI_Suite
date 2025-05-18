
import streamlit as st

def run():
    st.title("📈 Donation Goal Tracker")

    goal = 250000
    current = 168000
    percent = current / goal

    st.metric("Campaign Goal", f"${goal:,}")
    st.metric("Raised So Far", f"${current:,}")
    st.progress(percent)

    st.markdown("### Milestones")
    st.info("🎯 Hit $100K on May 20")
    st.warning("📢 $82K to go — time for mid-year push")
