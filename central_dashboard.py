
import streamlit as st

def run():
    st.title("🏟️ Venture North Control Panel")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("YTD Revenue", "$672,500")
        st.metric("Total Members", "2,450")
    with col2:
        st.metric("Upcoming Events", "16")
        st.metric("Expiring Sponsorships", "4")

    st.markdown("Use the sidebar to access detailed tools and reports.")
