
import streamlit as st

def run():
    st.set_page_config(page_title="Investor Portal", layout="wide")
    st.title("📊 Venture North Investor Portal")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("YTD Revenue", "$687,200")
        st.metric("Sponsor Revenue", "$172,300")
    with col2:
        st.metric("Utilization (Avg)", "82%")
        st.metric("Active Contracts", "18")

    st.markdown("### Tiered Sponsorship Overview")
    st.markdown("- Platinum: $30K+ | 4 Active")
    st.markdown("- Gold: $15K+ | 5 Active")
    st.markdown("- Silver: $5K+ | 6 Active")
    st.markdown("- Bronze: <$5K | 3 Active")

    st.markdown("### Downloads + Decks")
    st.download_button("📄 Download 1-Page Financial Summary", "Sample PDF content".encode(), file_name="venture_north_summary.pdf")
    st.markdown("🔗 [View Online Flipbook](https://flippingbook.com/your-deck)")
