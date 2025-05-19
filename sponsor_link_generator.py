
import streamlit as st

def run():
    st.title("🔗 Sponsor Link Generator")

    st.markdown("Create shareable links for your pitch deck, proposal, or portal access.")

    name = st.text_input("Sponsor Name", "TechNow")
    asset = st.selectbox("Target Asset", ["Turf", "Court 1", "Scoreboard", "Banner", "Dome Naming"])
    link_type = st.selectbox("Link Type", ["Proposal PDF", "Flipbook Pitch", "Sponsor Portal Access"])

    if link_type == "Proposal PDF":
        url = f"https://yourdomain.com/pdfs/{name.lower()}_proposal.pdf"
    elif link_type == "Flipbook Pitch":
        url = "https://flippingbook.com/your-deck"
    elif link_type == "Sponsor Portal Access":
        url = "https://yourdomain.com/sponsor-portal"

    st.code(url, language="markdown")
    st.download_button("📋 Copy Link to Share", url.encode(), file_name=f"{name}_link.txt")

    st.info("✅ Use this link in SMS, email, or Slack. Update domain as needed.")
