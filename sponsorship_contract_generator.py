import streamlit as st

def run():
    st.title("📄 Sponsorship Contract Generator")

    sponsor = st.text_input("Sponsor Name")
    asset = st.text_input("Sponsored Asset")
    value = st.number_input("Contract Value ($)", min_value=0, value=10000)
    term = st.selectbox("Contract Term", ["3 months", "6 months", "12 months", "Custom"])
    tier = st.selectbox("Tier", ["Platinum", "Gold", "Silver", "Bronze"])
    notes = st.text_area("Additional Terms")

    if st.button("Generate Contract Summary"):
        summary = f"""
Sponsor: {sponsor}
Asset: {asset}
Value: ${value}
Tier: {tier}
Term: {term}
Notes: {notes}
"""
        st.download_button("Download Contract Summary", summary.encode(), file_name="sponsor_contract.txt")