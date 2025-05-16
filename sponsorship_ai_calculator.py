import streamlit as st

def run():
    st.title("🤖 Sponsorship AI Calculator")

    value = 0
    assets = {
        "Court Banner ($2500)": 2500,
        "Turf Naming ($10,000)": 10000,
        "Digital Ad ($1500)": 1500
    }

    st.markdown("Select Assets:")
    selected = [k for k in assets if st.checkbox(k)]
    for k in selected:
        value += assets[k]

    visibility = st.slider("Visibility (1-10)", 1, 10, 5)
    exclusivity = st.slider("Exclusivity (1-10)", 1, 10, 5)
    duration = st.slider("Months", 1, 36, 12)

    multiplier = 1 + (visibility + exclusivity) / 20
    estimated = value * multiplier * (duration / 12)
    tier = "Platinum" if estimated > 50000 else "Gold" if estimated > 25000 else "Silver"

    st.metric("📈 Estimated Value", f"${estimated:,.2f}")
    st.success(f"Suggested Tier: {tier}")