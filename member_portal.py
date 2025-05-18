
import streamlit as st

def run():
    st.title("👤 Member Portal")

    member = "Jordan Smith"
    tier = "Gold"
    credits = 4
    events = ["Volleyball - Fri 6pm", "Turf Rental - Sun 3pm"]

    st.markdown(f"**Member:** {member}")
    st.markdown(f"**Tier:** {tier}")
    st.metric("Credits Remaining", credits)

    st.markdown("### Upcoming Bookings")
    for e in events:
        st.markdown(f"- {e}")

    st.markdown("Need more credits?")
    st.button("💳 Purchase Add-On Package")
