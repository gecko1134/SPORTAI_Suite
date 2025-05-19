
import streamlit as st

def run():
    st.set_page_config(page_title="Sponsor with Us", layout="wide")
    st.title("🤝 Become a Venture North Sponsor")

    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/Green_meadow.jpg", use_column_width=True)

    st.markdown("### Why Sponsor?")
    st.markdown("""
- 🏟 Access 250K+ annual park visitors
- 📣 Brand visibility across events, uniforms, scoreboards
- 💼 Multiple tiers + custom options
- 🎯 High-ROI regional exposure
""")

    st.markdown("### Get Started")
    name = st.text_input("Your Name")
    org = st.text_input("Organization")
    email = st.text_input("Email")
    interest = st.selectbox("Interested In:", ["Court", "Turf", "Team", "Tournament", "Naming Rights", "Other"])

    if st.button("Request Info Packet"):
        st.success("✅ Thanks! A sponsorship specialist will reach out within 24 hours.")

    st.markdown("🔗 [View Pitch Deck](https://flippingbook.com/your-deck)")
    st.download_button("📄 Download PDF Packet", "Sponsor packet content".encode(), file_name="venture_north_pitch.pdf")
