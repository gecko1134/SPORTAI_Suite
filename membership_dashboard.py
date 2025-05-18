
import streamlit as st
import pandas as pd

def run():
    st.title("👥 Membership Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Active Members", "2,540")
        st.metric("New Signups This Month", "112")
    with col2:
        st.metric("Average Credits Used", "78%")
        st.metric("Renewal Rate", "84%")

    st.markdown("### Membership Tier Breakdown")
    data = pd.DataFrame({
        "Tier": ["Basic", "Silver", "Gold", "Elite"],
        "Members": [1200, 800, 400, 140],
        "Avg Credits Used (%)": [60, 72, 85, 91],
        "Retention Rate (%)": [70, 75, 88, 93]
    })
    st.dataframe(data)

    st.markdown("### Activity Trends")
    chart_data = pd.DataFrame({
        "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "Check-ins": [430, 512, 498, 550],
        "Redemptions": [120, 135, 128, 150]
    }).set_index("Week")
    st.line_chart(chart_data)

    st.markdown("### Quick Insights")
    st.info("🔄 84% of Silver members renewed last quarter.")
    st.success("🎯 Gold and Elite tiers have >85% retention.")
    st.warning("📉 Basic tier shows lower credit usage — suggest promo campaign.")
