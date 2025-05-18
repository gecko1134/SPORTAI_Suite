
import streamlit as st
import datetime

def run():
    st.title("📅 Weekly Report Generator")

    st.markdown("### Summary Metrics")
    st.metric("Total Check-ins", "1,340", delta="↑ 6%")
    st.metric("Sponsorship Revenue", "$24,500", delta="↑ 10%")
    st.metric("Contract Renewals", "3 this week", delta="✓")

    st.markdown("### Suggested Email Content")
    today = datetime.date.today()
    st.code(f"""
Subject: Venture North Weekly Summary - {today.strftime('%B %d, %Y')}

Hello Board Members,

Here is your weekly operations snapshot:

- Total Check-ins: 1,340 (+6%)
- Sponsorship Revenue: $24,500 (+10%)
- Contracts Renewed: 3

Download full dashboard reports at your admin portal.

- Venture North Admin Suite
""", language="markdown")

    st.success("This report is ready to email or include in board PDFs.")
