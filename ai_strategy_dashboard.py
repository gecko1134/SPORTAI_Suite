
import streamlit as st

def run():
    st.title("🧠 AI Strategy Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Court Utilization", "82%", delta="↑ 6%")
        st.success("🏀 Court 3 fully booked this weekend")
    with col2:
        st.metric("Turf Utilization", "76%", delta="↑ 4%")
        st.info("⚽ Half Turf open Friday 2–5pm")
    with col3:
        st.metric("Sponsor Revenue YTD", "$162,400", delta="↑ $12K")
        st.warning("📢 3 contracts expiring this month")

    st.markdown("### Upcoming AI Suggestions")
    st.markdown("- Add Tue/Thu Adult Rec League (Court 2: idle 6–8pm)")
    st.markdown("- Promote Half Turf 3–5pm block for private rentals")
    st.markdown("- Offer 15% off scoreboard ad bundle for new sponsor")
