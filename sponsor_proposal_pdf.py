
import streamlit as st
from fpdf import FPDF
import tempfile

def run():
    st.title("📄 Sponsor Proposal Generator")

    name = st.text_input("Sponsor Name", "TechNow")
    asset = st.selectbox("Asset", ["Court 1", "Turf", "Scoreboard", "Banner", "Naming Rights"])
    tier = st.selectbox("Tier", ["Bronze", "Silver", "Gold", "Platinum"])
    value = st.number_input("Proposal Value ($)", 500, 100000, 15000)
    term = st.slider("Duration (months)", 1, 36, 12)

    if st.button("Generate Proposal PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.multi_cell(0, 10, f"Sponsorship Proposal: {name}")
        pdf.set_font("Arial", "", 12)
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"Asset Sponsored: {asset}")
        pdf.multi_cell(0, 8, f"Sponsorship Tier: {tier}")
        pdf.multi_cell(0, 8, f"Proposal Value: ${value:,}")
        pdf.multi_cell(0, 8, f"Term: {term} months")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp.seek(0)
            st.download_button("📥 Download Proposal PDF", tmp.read(), file_name=f"{name}_proposal.pdf")
