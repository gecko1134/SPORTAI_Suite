import streamlit as st
def run():
    st.title("📖 Flipbook Viewer")
    url = st.text_input("Paste Flipbook Embed URL")
    if url:
        st.markdown(f"<iframe src='{url}' width='700' height='400'></iframe>", unsafe_allow_html=True)