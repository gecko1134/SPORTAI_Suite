
import streamlit as st
import json
from pathlib import Path

def run():
    st.title("🏗️ Multi-Org Setup Assistant")

    name = st.text_input("Organization Name")
    region = st.text_input("Region")
    email = st.text_input("Admin Contact Email")

    sponsors = st.checkbox("Enable Sponsor Suite", value=True)
    donors = st.checkbox("Enable Donor Suite", value=True)
    grants = st.checkbox("Enable Grant Tracking", value=True)
    crm = st.checkbox("Enable CRM Features", value=True)
    board = st.checkbox("Enable Board Reporting", value=True)

    if st.button("Generate Config"):
        config = {
            "organization": name,
            "region": region,
            "contact_email": email,
            "modules_enabled": {
                "sponsors": sponsors,
                "donors": donors,
                "grants": grants,
                "crm": crm,
                "board_reporting": board
            }
        }
        Path("platform_config.json").write_text(json.dumps(config, indent=2))
        st.success("✅ platform_config.json created. Copy it into the root of your app.")
