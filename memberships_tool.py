import streamlit as st
import pandas as pd

def run():
    st.title("👥 Membership Dashboard")

    data = pd.DataFrame({
        "Member": ["Jordan", "Casey", "Taylor"],
        "Tier": ["Elite", "Family", "Basic"],
        "Credits": [50, 30, 10],
        "Used": [35, 15, 4],
    })

    data["Remaining"] = data["Credits"] - data["Used"]
    selected_tier = st.selectbox("Filter by Tier", ["All"] + data["Tier"].unique().tolist())
    if selected_tier != "All":
        data = data[data["Tier"] == selected_tier]

    st.dataframe(data)
    st.download_button("Download CSV", data.to_csv(index=False), "members.csv")