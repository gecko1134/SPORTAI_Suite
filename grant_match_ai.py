
import streamlit as st

def run():
    st.title("🔍 AI Grant Match Engine")

    category = st.selectbox("Select Focus Area", [
        "Youth Sports", "Adaptive Access", "Esports", "Facility Expansion",
        "Trails & Environment", "Tourism Development", "Community Health"
    ])

    st.markdown("### Suggested Grants:")
    if category == "Youth Sports":
        st.success("🏆 'Play60 Foundation Grant' – youth-focused equipment and field access")
    elif category == "Adaptive Access":
        st.success("♿ 'Inclusive Rec Fund' – accessible facility upgrades")
    elif category == "Esports":
        st.success("🎮 'Digital Arena Grant' – technology expansion for public access esports")
    elif category == "Facility Expansion":
        st.success("🏗 'State Infrastructure Bond' – dome and utility funding")
    elif category == "Trails & Environment":
        st.success("🌿 'Green Recreation Fund' – trail and energy-efficient upgrades")
    elif category == "Tourism Development":
        st.success("🧳 'Tourism Grant Program' – travel sports and regional exposure funding")
    elif category == "Community Health":
        st.success("🧍 'Active Living Challenge Grant' – events and free-use programming")

    st.info("⚙️ AI auto-matches grants based on facility goals, program types, and region.")
