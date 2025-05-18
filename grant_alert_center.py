
import streamlit as st
from datetime import date

def run():
    st.title("📣 Grant Alert Center")

    st.markdown("### Upcoming Deadlines + Actions")
    st.warning("📆 Tourism Grant due July 15 — finalize attachments")
    st.success("💵 Green Rec Fund approved — move to accounting sync")
    st.info("🔁 Play60 reapply window opens Aug 1")

    st.markdown("### Contact Reminders")
    st.markdown("- 📩 Email grant@foundation.org for Q2 progress form")
    st.markdown("- 🗂 Attach receipts to Adaptive Fund submission before 6/30")
