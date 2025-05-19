
import streamlit as st
from fpdf import FPDF
import tempfile
from datetime import date

def run():
    st.title("📄 Full Board Packet PDF Generator")

    today = date.today().strftime("%B %d, %Y")
    revenue = 687200
    expenses = 412300
    net = revenue - expenses

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, f"Board Report – Venture North Sports Park")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)

    pdf.multi_cell(0, 8, f"Date: {today}")
    pdf.multi_cell(0, 8, f"YTD Revenue: ${revenue:,}")
    pdf.multi_cell(0, 8, f"Operating Costs: ${expenses:,}")
    pdf.multi_cell(0, 8, f"Net Operating Margin: ${net:,}")

    pdf.ln(5)
    pdf.multi_cell(0, 8, "Sponsor Summary:
- 18 Active Deals
- 3 Expiring
- Total Value: $172,300")

    pdf.ln(5)
    pdf.multi_cell(0, 8, "Grant Status:
- 5 Tracked
- 2 Approved
- 1 Reapply window opens August")

    pdf.ln(5)
    pdf.multi_cell(0, 8, "Upcoming Events:
- Youth Tournament: June 15
- Adaptive Expo: July 1")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp.seek(0)
        st.download_button("📥 Download Board Packet", tmp.read(), file_name="board_packet_summary.pdf")
