
import streamlit as st

def run():
    st.title("🎪 Non-Sports Event Templates")

    st.markdown("### Common Event Configs")
    event = st.selectbox("Select Event Type", [
        "Wedding", "Reunion", "Robotics Competition", "Archery Tournament",
        "Fishing Expo", "Arts & Crafts Show", "Sports Card Show", "Food Expo"
    ])

    if event == "Wedding":
        st.success("Reserve full dome, disable scoreboard, add 6 staff")
    elif event == "Robotics Competition":
        st.info("Use 2 courts with tables, allow access to power, restrict ball sports")
    elif event == "Fishing Expo":
        st.info("Reserve ½ dome + sponsor booth areas + community pavilion")
    elif event == "Arts & Crafts Show":
        st.info("Use full turf with vendor lanes and entry table bundles")

    st.warning("Ensure staff checklists & layout map are attached before confirmation.")
