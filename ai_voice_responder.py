
import streamlit as st

def run():
    st.title("🎙️ Voice Assistant Simulator")

    st.markdown("Simulate real-time Q&A from facility ops team:")

    query = st.text_input("Ask something like 'What’s underused tomorrow?' or 'Show expiring contracts'")

    if query:
        if "underused" in query.lower():
            st.warning("Court 4 and Half Turf are under 50% booked this weekend.")
        elif "expiring" in query.lower():
            st.info("BankCo (Scoreboard) expires in 10 days. Nike (Court 1) expires next month.")
        elif "check-ins" in query.lower():
            st.success("Today: 438 check-ins. This week: 2,190.")
        elif "sponsors" in query.lower():
            st.success("16 active, 2 pending, 3 expiring this quarter.")
        else:
            st.error("Sorry, I couldn’t interpret that. Try again with a usage, forecast, or contract query.")
