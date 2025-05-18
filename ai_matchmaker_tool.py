
import streamlit as st

def run():
    st.title("🧠 AI Matchmaker Tool")

    st.markdown("### Find Team/Program Matches by Skill or Category")
    category = st.selectbox("Select Program Type", ["Youth", "Adult", "Elite", "Special Needs"])
    skill = st.slider("Skill Level (1 = Beginner, 5 = Advanced)", 1, 5, 3)
    sport = st.selectbox("Sport", ["Basketball", "Soccer", "Volleyball", "Flag Football", "Pickleball"])

    if st.button("Find Matches"):
        st.success(f"Showing top matches for {sport} - {category} level {skill}")
        st.markdown("- Team Alpha (skill 3.2) ⚽\n- Court Crushers (skill 3.5) 🏀\n- Flex Play Club (skill 2.9) 🏐")
