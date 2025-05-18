
import streamlit as st

def run():
    st.title("👥 Facility Membership Monitor")
    st.markdown("Breakdown of member types and usage.")
    st.metric("Active Members", "2,550")
    st.metric("Average Visits per Week", "3.4")
    st.success("85% of Silver members used credits in past 30 days.")
    st.warning("Gold tier below goal – push campaign with bonus incentive.")
