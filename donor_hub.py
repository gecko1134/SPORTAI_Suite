
import streamlit as st

def run():
    st.title("🎁 Donor Engagement Hub")

    st.markdown("Welcome to the Venture North donor tools center.")

    st.markdown("### Quick Access Tools")
    if st.button("👤 Create Donor Profile"):
        st.switch_page("donor_profile_creator.py")
    if st.button("🔍 Find Donor Match"):
        st.switch_page("donor_match_ai.py")
    if st.button("💬 Generate Message"):
        st.switch_page("donor_message_builder.py")
    if st.button("📈 Track Fundraising Goal"):
        st.switch_page("donation_goal_tracker.py")
    if st.button("💳 Open Checkout"):
        st.switch_page("donation_checkout.py")
    if st.button("🎯 View Campaign Summary"):
        st.switch_page("donation_campaign_viewer.py")

    st.markdown("---")
    st.info("Use this hub to streamline donor communication, giving, and tracking.")
