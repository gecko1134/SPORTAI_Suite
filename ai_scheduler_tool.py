import streamlit as st

def run():
    st.title("🧠 AI Scheduler")
    gaps = {
        "Court 1": ["11am", "1pm"],
        "Turf": ["2pm", "3pm"],
    }

    for surface, hours in gaps.items():
        st.info(f"{surface} has gaps at: {', '.join(hours)}")
        st.write("💡 Suggest: Open session or discounted booking")