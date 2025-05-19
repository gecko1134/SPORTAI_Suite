
import streamlit as st
from datetime import date

def run():
    st.title("💼 Investor Packet Generator")

    today = date.today().strftime("%B %d, %Y")
    name = st.text_input("Investor Name", "Venture Partners LLC")
    value = 260150
    highlight = "Youth turf & trail expansion funded 74% to goal"

    st.markdown("### Investor Summary Packet")
    st.markdown(f"**Prepared For:** {name}")
    st.markdown(f"**Date:** {today}")
    st.metric("YTD Operating Margin", f"${value:,}")
    st.success(f"📈 Highlight: {highlight}")

    st.markdown("📥 Attach proposal PDF and ROI tracker to investor-facing email.")
    st.download_button("Download Summary", f"{name} summary for {today}".encode(), file_name="investor_summary.txt")
