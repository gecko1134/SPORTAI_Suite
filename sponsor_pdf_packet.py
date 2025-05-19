
import streamlit as st
from fpdf import FPDF
import tempfile

def run():
    st.title("📄 Branded Sponsor Packet Generator")

    org = st.text_input("Complex Name", "Venture North Sports Park")
    logo = st.text_input("Logo URL (optional)")
    contact = st.text_input("Contact Email", "sponsor@venturenorth.org")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{org} Sponsorship Packet", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    pdf.multi_cell(0, 8, """
Tiers:

Platinum ($30K+): Dome, turf, scoreboard
Gold ($15K+): Court + banner + tournament
Silver ($5K+): Uniform, digital bundle
Bronze (<$5K): Booths, program insertions

Your brand supports:
- Youth access and scholarships
- National tournaments
- Community events

Contact us today!
""")
    pdf.cell(0, 10, f"Email: {contact}", ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp.seek(0)
        st.download_button("📥 Download Sponsor Packet PDF", tmp.read(), file_name="sponsor_packet.pdf")
