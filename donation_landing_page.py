
import streamlit as st

def run():
    st.set_page_config(page_title="Support Venture North", layout="wide")
    st.title("🌟 Support the Park")

    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/Green_meadow.jpg", use_column_width=True)

    st.markdown("## Help us expand access, community, and excellence.")
    st.markdown("Your donation supports youth programs, adaptive access, scholarships, and facility upgrades.")

    goal = 250000
    current = 186450
    percent = current / goal

    st.progress(percent)
    st.metric("Raised So Far", f"${current:,}")
    st.metric("Goal", f"${goal:,}")

    st.markdown("### Choose Your Impact")
    st.markdown("- 🧍 Adaptive Sports Access")
    st.markdown("- 🏀 Court Upgrades")
    st.markdown("- 🧑‍🎓 Youth Scholarships")
    st.markdown("- 🏕 Trail Enhancements")

    st.markdown("### Ready to Donate?")
    st.markdown("[💳 Click here to donate via Stripe](https://buy.stripe.com/test_4gw5no3Fkgds3kUaEE)")
