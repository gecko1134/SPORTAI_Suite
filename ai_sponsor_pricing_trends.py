
import streamlit as st

def run():
    st.title("📈 AI Sponsor Pricing Trend Monitor")

    st.markdown("### Regional & National Pricing Benchmarks (Est.)")

    st.markdown("""
| Asset | Regional Avg | National Avg |
|-------|--------------|--------------|
| Dome Naming | $50K–$150K | $250K–$500K+ |
| Court | $3K–$10K | $10K–$25K |
| Turf | $10K–$25K | $30K–$50K |
| Scoreboard | $3K–$7K | $10K–$15K |
| Banner | $500–$2K | $2K–$5K |
| Tournament | $5K–$25K | $10K–$50K+ |
""", unsafe_allow_html=True)

    st.markdown("### Current Park Rate Suggestions")
    st.info("🏷 Court 1: currently at $5,000/yr → hold")
    st.success("⚽ Full Turf: 93% booked + tournament exposure → consider increasing to $22,000")
    st.warning("📉 Wall banners $600 – consider raising to $1,200 with sponsor demand")

    st.success("AI recommends testing new bundles for mid-tier sponsors using digital ads + onsite placement.")
