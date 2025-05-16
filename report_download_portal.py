import streamlit as st
def run():
    st.title("Download Reports")
    st.download_button("Download PDF", "Report".encode(), "report.pdf")