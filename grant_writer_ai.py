
import streamlit as st
from datetime import date

def run():
    st.title("✍️ AI Grant Writing Assistant")

    program = st.text_input("Program Name", value="Youth Sports Access")
    amount = st.number_input("Funding Request ($)", 1000, 100000, 10000)
    focus = st.selectbox("Focus Area", ["Youth", "Adaptive", "Facility", "Tech", "Health"])
    goal = st.text_area("What does the grant support?", "Expand free turf access for youth rec leagues.")

    today = date.today().strftime("%B %d, %Y")

    summary = f"""
**Grant Narrative – {program}**

As of {today}, Venture North seeks ${amount:,} in funding to support our mission in {focus.lower()} development. Specifically, this proposal supports:

- {goal}
- Inclusive community access
- Measurable outcomes via participation and impact tracking

Thank you for your consideration.

– Venture North Development Team
"""

    st.markdown("### Generated Summary")
    st.text_area("Grant Summary", summary, height=250)
    st.download_button("📄 Download Narrative", summary.encode(), file_name="grant_summary.txt")
