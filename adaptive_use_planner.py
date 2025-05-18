
import streamlit as st

def run():
    st.title("🔄 Adaptive Use Planner")

    st.markdown("### Smart Surface Conversions")
    surface = st.selectbox("Select a Surface", ["Half Turf", "Court 2", "Full Turf", "Court 4"])

    if surface == "Half Turf":
        st.success("💍 Convert to wedding layout + vendor lanes on weekends")
    elif surface == "Court 2":
        st.info("🎮 Ideal for esports or robotics zones (quiet + power access)")
    elif surface == "Full Turf":
        st.success("🎪 Host archery or multi-booth expo — prime weekend space")
    elif surface == "Court 4":
        st.warning("📉 Underused – test temporary pickleball or crafts layout")

    st.markdown("Use adaptive conversion to keep the park running at 90%+ utilization.")
