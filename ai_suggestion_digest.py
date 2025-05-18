
import streamlit as st
from datetime import date

def run():
    st.title("📬 AI Suggestion Digest")

    st.markdown(f"### Recommendations for {date.today().strftime('%A, %B %d')}")

    st.success("✅ Offer Half Turf rental at 20% discount during 2–4pm (low fill block)")
    st.warning("⚠️ Scoreboard sponsorship expires in 18 days — prep renewal packet")
    st.info("💡 Court 4 has consistent underuse at 10–11am – add youth rec promo")
    st.success("✅ Email follow-up to BankCo after last event (ROI was 185%)")
    st.info("💡 Saturday 9am–12pm unbooked on Court 2 — bundle with banner ad")
    st.warning("⚠️ Dana (volunteer) needs re-credentialing before next tournament")
    st.success("✅ Social post performed well — replicate ad copy for July")

    st.markdown("Use this digest for weekly staff review or to auto-load tasks into Slack/Calendar.")
