
import streamlit as st
import json
from pathlib import Path

def run():
    st.set_page_config(page_title="Welcome", layout="wide")

    config_path = Path("platform_config.json")
    if config_path.exists():
        config = json.loads(config_path.read_text())
    else:
        st.error("platform_config.json not found.")
        return

    st.title(f"🏟️ Welcome to {config['organization']}")
    st.caption(f"Region: {config['region']}")

    st.markdown("### What would you like to do?")
    if config["modules_enabled"].get("sponsors"):
        st.page_link("sponsor_pitch_portal.py", label="💼 Sponsorship Portal")
    if config["modules_enabled"].get("donors"):
        st.page_link("donation_landing_page.py", label="🎁 Donate Now")
    if config["modules_enabled"].get("grants"):
        st.page_link("grant_match_ai.py", label="🔍 Grant Match Engine")
    if config["modules_enabled"].get("crm"):
        st.page_link("crm_pipeline_dashboard.py", label="📊 CRM Dashboard")
    if config["modules_enabled"].get("board_reporting"):
        st.page_link("board_packet_pdf_generator.py", label="📄 Board Reports")

    st.markdown("---")
    st.markdown(f"📬 Contact: {config['contact_email']}")
