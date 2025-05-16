import streamlit as st
def run():
    st.title("🧠 Setup Assistant AI")
    st.write("Let’s customize your Venture North platform.")
    st.radio("What is your primary use?", ["Sports Rentals", "Tournaments", "Events", "Mixed"])