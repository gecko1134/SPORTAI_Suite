
import streamlit as st

def run():
    st.title("📄 PandaDoc Contract Preview")

    st.markdown("This tool would connect to PandaDoc to send sponsor or lease contracts.")
    st.info("Add company name, duration, value, and click 'Send via PandaDoc'.")
    st.warning("SendGrid + PandaDoc API keys required.")
