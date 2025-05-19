
import streamlit as st
from datetime import date

def run():
    st.title("🔄 Fundraising Narrative Sync")

    today = date.today().strftime("%B %d, %Y")

    st.markdown("### Latest Sync Snapshot")
    st.info(f"📅 Narrative pulled on {today}")
    st.success("💵 Raised $184,750 toward $250K turf + trail expansion")
    st.warning("⚠️ Grant Tourism Renewal due in 5 days")

    st.markdown("### Synced Narrative:")
    st.text_area("Narrative Block", f"""
As of {today}, Venture North has secured $184,750 in donations and grants toward a $250,000 expansion goal. Key milestones include:

- Grant approvals from Play60 and Green Rec Fund
- Sponsorships from TechNow, BankCo, and HealthCo
- Adaptive programming expansion scheduled for July

This positions us for continued funding growth and final push campaigns this summer.
""", height=250)
