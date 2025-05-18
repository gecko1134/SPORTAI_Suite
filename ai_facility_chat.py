
import streamlit as st

def run():
    st.title("🧠 AI Facility Assistant (Chat Mode)")

    st.markdown("Ask anything about the complex. Try questions like:")
    st.markdown("- 'How many check-ins today?'
- 'Show me underused courts.'
- 'Generate sponsor proposal for TechNow.'")

    query = st.text_input("Type your command")

    if query:
        if "check-in" in query.lower():
            st.success("✅ 438 check-ins today. 2,170 this week.")
        elif "underused" in query.lower():
            st.warning("⚠️ Court 4 is 41% booked. Suggest youth drop-in from 3–5pm.")
        elif "sponsor" in query.lower() and "proposal" in query.lower():
            st.success("📄 Sponsor proposal for TechNow: Turf + Scoreboard + Digital Ad = $12,000 package.")
        elif "forecast" in query.lower():
            st.info("📅 Saturday forecast: 19 events, 740 guests. Turf is 100% booked. Court 2 has open 4–6pm block.")
        else:
            st.error("🤖 Sorry, I didn’t catch that. Try asking about usage, revenue, or schedules.")
