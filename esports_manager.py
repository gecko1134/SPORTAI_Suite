
import streamlit as st
import pandas as pd

def run():
    st.title("🎮 Esports Manager")

    df = pd.DataFrame({
        "Team": ["Game Titans", "Rocket Pros", "Valor Kings"],
        "Game": ["Fortnite", "Rocket League", "Valorant"],
        "Age Group": ["HS", "College", "College"],
        "Rank": ["Diamond", "Champ II", "Immortal"],
        "Region": ["North", "Central", "East"]
    })
    st.dataframe(df)

    st.markdown("### Scheduling Tip")
    st.info("🕹️ Rocket League teams prefer Fri 6–10pm and Sat AM sessions.")
