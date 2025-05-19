
import streamlit as st
from datetime import datetime

def run():
    st.title("📅 Automated Board Report Scheduler")

    st.markdown("Select timing + content for auto-reports:")

    frequency = st.selectbox("Report Frequency", ["Weekly", "Monthly", "Quarterly"])
    delivery_method = st.selectbox("Delivery Method", ["Download Only", "SendGrid Email", "Slack Channel"])

    sections = st.multiselect("Sections to Include", [
        "YTD Revenue",
        "Sponsor Activity",
        "Upcoming Events",
        "Usage Breakdown",
        "Grant Status",
        "Board Action Items"
    ], default=["YTD Revenue", "Sponsor Activity", "Grant Status"])

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.success(f"✅ Report scheduled for {frequency} delivery starting {now} via {delivery_method}.")
