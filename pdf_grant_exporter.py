
import streamlit as st
from fpdf import FPDF
import tempfile
import os

def run():
    st.title("📄 Grant PDF Generator")

    title = st.text_input("Document Title", "Youth Sports Access Narrative")
    body = st.text_area("Narrative Content", "This grant supports expansion of turf access for underserved youth...")

    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.multi_cell(0, 10, title)
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, body)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp.seek(0)
            btn = st.download_button("📥 Download PDF", tmp.read(), file_name="grant_narrative.pdf")
