
import streamlit as st

def run():
    st.set_page_config(page_title="Investor Access", layout="wide")
    st.title("🔐 Venture North Investor Portal")

    pwd = st.text_input("Enter Access Code", type="password")
    if pwd != "venturenorth2024":
        st.warning("🔐 Investor access only. Please enter a valid code.")
        return

    st.success("✅ Access granted")
    st.metric("YTD Revenue", "$687,200")
    st.metric("Sponsor Revenue", "$172,300")
    st.metric("Net Margin", "$260,150")
    st.markdown("### Documents:")
    st.download_button("📄 Financial Summary", "Investor Finance Summary PDF".encode(), file_name="investor_summary.pdf")
    st.markdown("🔗 [Pitch Deck Flipbook](https://flippingbook.com/your-deck)")
