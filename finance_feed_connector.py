
import streamlit as st

def run():
    st.title("🔗 Real-Time Finance Feed Connector")

    st.markdown("Configure export of revenue + expenses to your accounting system.")

    export_type = st.selectbox("Export Format", ["Google Sheets", "CSV for QuickBooks", "Xero API (Coming Soon)"])
    st.text_input("Target Export File / Sheet URL")

    st.markdown("### Sample Categories Synced:")
    st.markdown("- Rentals: Court, Turf, Equipment")
    st.markdown("- Events: Tournaments, Non-Sports Bookings")
    st.markdown("- Sponsors: Contracts, Packages, Add-ons")
    st.markdown("- Ops: Staff, Setup, Utilities, Insurance")

    st.success("Ready to configure your live accounting export pipeline.")
