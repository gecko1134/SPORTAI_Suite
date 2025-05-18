
import streamlit as st
import pandas as pd

def run():
    st.title("📊 Real-Time Admin Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Check-ins Today", "438")
        st.metric("Court Usage %", "82%")
    with col2:
        st.metric("Revenue Today", "$4,920")
        st.metric("Events Scheduled", "15")

    st.markdown("### Surface Overview")
    usage = pd.DataFrame({
        "Surface": ["Court 1", "Court 2", "Turf A", "Court 3", "Court 4"],
        "Utilization (%)": [88, 76, 93, 59, 49]
    })
    st.dataframe(usage)

    st.markdown("### AI Digest Highlights")
    st.success("🏀 Court 3 trending underused – rec league suggested")
    st.warning("⚠️ 3 sponsor contracts expiring this month")
    st.info("📈 Full Turf booked all weekend – consider price bump")

    st.markdown("### Report Tools")
    st.markdown("- [ ] Download PDF summary")
    st.markdown("- [ ] Send Weekly Report to Board")
