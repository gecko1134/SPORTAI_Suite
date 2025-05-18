
import streamlit as st
import pandas as pd

def run():
    st.title("💰 Event Profitability Analyzer")

    df = pd.DataFrame({
        "Event": ["Youth Soccer Tourney", "Fishing Expo", "HS Volleyball Classic", "Vendor Market"],
        "Revenue ($)": [8200, 4000, 6700, 3500],
        "Costs ($)": [4200, 6000, 3500, 2900],
    })
    df["Profit ($)"] = df["Revenue ($)"] - df["Costs ($)"]
    df["Result"] = df["Profit ($)"].apply(lambda x: "✅ Positive" if x > 0 else "🛑 Negative")
    st.dataframe(df)

    st.markdown("### AI Observations")
    st.success("🏐 HS Volleyball Classic net $3,200 – run again next quarter.")
    st.warning("🎣 Fishing Expo lost $2,000 – review marketing strategy or move to fall.")
