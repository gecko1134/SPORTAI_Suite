
import streamlit as st
import json
from pathlib import Path

def run():
    config_path = Path("platform_config.json")
    if config_path.exists():
        config = json.loads(config_path.read_text())
        st.markdown(f"### {config['organization']} – {config['region']}")
        st.caption(f"Contact: {config['contact_email']}")
