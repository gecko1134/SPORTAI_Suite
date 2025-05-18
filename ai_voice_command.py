
import streamlit as st

def run():
    st.title("🎙️ AI Command Assistant")

    st.markdown("Type a command below to simulate a voice interface:")

    command = st.text_input("Ask a question or give a command")

    if st.button("Execute"):
        if "underused" in command or "idle" in command:
            st.info("Court 4 is under 40% booked. Suggest rec league or drop-in block.")
        elif "best time for volleyball" in command.lower():
            st.success("Best slot: Court 3, Tue & Thu 6–8pm (high availability + low overlap)")
        elif "expiring sponsor contracts" in command:
            st.warning("3 sponsor contracts expiring in next 30 days: BankCo, Scoreboard, Banner A")
        elif "revenue today" in command.lower():
            st.success("Today’s booked revenue: $4,520 across 5 surfaces.")
        elif "forecast for saturday" in command.lower():
            st.info("Saturday = 19 events, 700+ expected guests, 2 open blocks remain.")
        else:
            st.error("Sorry, I didn’t recognize that request. Try asking about usage, forecasts, or scheduling.")
