
import streamlit as st

def run():
    st.title("📦 Exportable Marketing Packet Builder")

    st.markdown("### Bundle Your Full Sponsor/Donor Pitch Tools")

    name = st.text_input("Campaign or Complex Name", "Venture North Sports Park")
    email = st.text_input("Contact Email", "sponsor@venturenorth.org")
    include_flipbook = st.checkbox("Include Flipbook Link")
    include_pdf = st.checkbox("Include Proposal PDF")
    include_map = st.checkbox("Include Asset Map Image")

    st.markdown("### Contents Preview")

    st.markdown(f"📍 Complex: **{name}**")
    st.markdown(f"📧 Contact: {email}")

    if include_flipbook:
        st.markdown("🔗 Flipbook: [View](https://flippingbook.com/your-deck)")
    if include_pdf:
        st.markdown("📄 Attached: sponsor_packet.pdf")
    if include_map:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Org_chart_structure.svg/800px-Org_chart_structure.svg.png")

    st.success("✅ Ready to download all pieces or compile ZIP manually.")
    st.download_button("📁 Export Summary TXT", f"{name} marketing summary".encode(), file_name="marketing_summary.txt")
