import streamlit as st

def run():
    st.title("📖 Flipbook + Pitch Deck Generator")

    template = st.selectbox("Choose Template", ["Sponsor Proposal", "Event Overview", "Expo Marketing Pack"])
    image = st.file_uploader("Upload Banner or Logo")
    desc = st.text_area("Describe the Event or Package")

    if st.button("Generate PDF"):
        st.success("✅ PDF and Flipbook file created.")
        st.markdown("🖇️ Embed code: `<iframe src='https://flippingbook.com/your-deck' width='600'></iframe>`")