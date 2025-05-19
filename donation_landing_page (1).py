
import streamlit as st

def run():
    st.set_page_config(page_title="Support Venture North", layout="wide")
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/12/Sport_event_logo_concept.png", width=200)

    st.title("🌟 Support Venture North")

    st.markdown("Help fund youth access, trail development, adaptive programs, and elite sports facilities.")

    st.subheader("Impact Goals")
    st.markdown("- 🏞 Expand trails and turf facilities")
    st.markdown("- 👨‍👩‍👧‍👦 Offer 1,000 scholarships")
    st.markdown("- ♿ Build inclusive sport infrastructure")

    st.subheader("Progress")
    goal = 250000
    current = 189400
    st.progress(current / goal)
    st.metric("Raised", f"${current:,}")
    st.metric("Goal", f"${goal:,}")

    st.markdown("### Donate or Sponsor Now")
    st.markdown("[💳 Click here to donate](https://your-checkout-link)")
    st.download_button("📄 Download PDF Pitchbook", "Sponsor pitch summary".encode(), file_name="venture_north_pitchbook.pdf")
