import streamlit as st
import pandas as pd

def run():
    st.title("🎁 Loyalty & Rewards Engine")

    rewards = pd.DataFrame({
        "Member": ["Jordan", "Casey", "Dana"],
        "Points": [180, 70, 115],
        "Eligible Reward": ["Free Rental", "Concession Credit", "Trainer Session"]
    })
    st.dataframe(rewards)
    st.info("📈 Jordan close to Elite Tier — show upsell")