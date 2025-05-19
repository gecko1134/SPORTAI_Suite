
import streamlit as st
import time

def run():
    st.title("🖼️ Media Display Rotator")

    images = [
        "https://upload.wikimedia.org/wikipedia/commons/5/51/Green_meadow.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Tennis_court.jpg/800px-Tennis_court.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Org_chart_structure.svg/800px-Org_chart_structure.svg.png"
    ]

    for img in images:
        st.image(img, use_column_width=True)
        time.sleep(15)
        st.empty()
