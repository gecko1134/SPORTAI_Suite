
import streamlit as st

def run():
    st.title("🏷 Sponsor Portal")

    sponsor = "TechNow"
    tier = "Platinum"
    assets = ["Half Turf", "Court 2 Banner", "Digital Wall Ad"]

    st.markdown(f"**Sponsor:** {sponsor}")
    st.markdown(f"**Tier:** {tier}")
    st.markdown("### Sponsored Assets:")
    for a in assets:
        st.markdown(f"- {a}")

    st.download_button("📄 Download Current Contract", "TechNow Sponsorship Contract.pdf".encode(), file_name="technow_contract.pdf")

    st.markdown("Need help or want to upgrade?")
    st.button("📞 Contact Sponsorship Manager")
