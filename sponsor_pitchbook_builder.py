
import streamlit as st

def run():
    st.title("📘 AI Sponsorship Pitchbook")

    st.markdown("### Suggested Tiers + Assets")
    st.markdown("""
**Platinum ($30K+)**
- Dome Naming Rights
- Turf Bundle (Full + Half)
- Digital Scoreboard Takeover

**Gold ($15K–$30K)**
- Court Naming
- Scoreboard + Wall Banner
- Tournament Title Sponsor

**Silver ($5K–$15K)**
- Wall Banners
- Social/Digital Packages
- Event Co-Host

**Bronze (< $5K)**
- Team Uniform Sponsor
- Equipment or In-Kind
- Vendor Booths / Expo Space
""")

    st.markdown("### ROI Highlights")
    st.success("⚽ Turf average 30K+ impressions/month (events + practices)")
    st.success("🏀 Court usage 85%+ — ideal for brand visibility")
    st.info("📣 Bundle digital + in-venue for 3X recall rate")

    st.download_button("📄 Download Pitch Summary", "Sample Sponsorship Pitchbook Content".encode(), file_name="sponsor_pitchbook.txt")
