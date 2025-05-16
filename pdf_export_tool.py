import streamlit as st
def run():
    st.title("📄 PDF Export Tool")
    st.download_button("Download Sample PDF", "PDF content here".encode(), file_name="summary.pdf")