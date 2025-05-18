
import streamlit as st

def run():
    st.title("📄 Board Financial Summary")

    st.markdown("### Current Financial Snapshot")
    st.metric("Total Revenue YTD", "$672,450")
    st.metric("Operating Costs YTD", "$412,300")
    st.metric("Net Operating Surplus", "$260,150")

    st.markdown("### Contract & Sponsorship Overview")
    st.markdown("- 16 Active Sponsorship Contracts")
    st.markdown("- 3 Expiring Within 30 Days")
    st.markdown("- 2 New Contracts Under Review")

    st.markdown("### Forecast Highlights")
    st.success("📈 Turf usage +12% this quarter → revenue spike expected")
    st.warning("📉 Basic member renewals down – marketing push needed")

    st.markdown("### Download Option (Coming Soon)")
    st.button("📥 Export PDF Financial Report")
