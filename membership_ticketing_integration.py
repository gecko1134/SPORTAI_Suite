import streamlit as st

def run():
    st.title("🎟️ Ticketing + Membership Integration")

    st.markdown("### Track Entry Logs")
    st.table([
        {"Member": "Jordan", "Event": "Esports Finals", "Method": "Phone QR", "Points Earned": 5},
        {"Member": "Casey", "Event": "Movie Night", "Method": "Fob", "Points": 3},
    ])

    st.info("📢 Casey earned enough for a 10% food credit!")