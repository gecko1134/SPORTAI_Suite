
import streamlit as st
import pandas as pd

def run():
    st.title("👥 Membership CRM + AI Insights")

    data = pd.DataFrame({
        "Member": ["Jordan", "Taylor", "Alex", "Sam", "Dana"],
        "Tier": ["Gold", "Silver", "Basic", "Gold", "Silver"],
        "Credits Remaining": [2, 8, 15, 1, 12],
        "Last Visit": ["2024-06-01", "2024-05-12", "2024-03-15", "2024-06-04", "2024-04-20"]
    })

    data["Status"] = "✅ Active"
    data.loc[data["Credits Remaining"] < 5, "Status"] = "⚠️ Low Credits"
    data.loc[pd.to_datetime(data["Last Visit"]) < pd.to_datetime("2024-05-01"), "Status"] = "🛑 At Risk"

    st.dataframe(data)

    st.markdown("### AI Recommendations")
    st.info("Jordan (Gold): Suggest Elite tier upsell")
    st.warning("Alex inactive since March — consider reactivation promo")
