
import streamlit as st

def run():
    st.title("💡 Smart Upsell Offer Engine")

    tier = st.selectbox("Current Tier", ["Basic", "Silver", "Gold", "Elite"])
    credits_used = st.slider("Credits Used This Month", 0, 30, 22)

    if credits_used >= 25:
        st.success("🎯 You’re almost out of credits! Upgrade to the next tier now and get 10% off.")
    elif tier == "Basic" and credits_used >= 10:
        st.info("💬 You’ve used 10+ credits this month. Consider switching to Silver for better value.")
    else:
        st.warning("🕒 You’re halfway through your credits. Watch for bundle deals soon!")
