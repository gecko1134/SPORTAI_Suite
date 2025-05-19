
import streamlit as st

def run():
    st.title("🛠️ Admin Override Console")

    st.warning("⚠️ Use caution — this console allows live data override.")

    revenue_input = st.number_input("Override YTD Revenue ($)", min_value=0, value=687200)
    sponsor_count = st.number_input("Override Sponsor Count", min_value=0, value=18)

    if st.button("Save Override"):
        st.success(f"Updated revenue to ${revenue_input:,} and sponsors to {sponsor_count}.")

    st.markdown("### Advanced Controls")
    if st.button("🔁 Reset Grant Timer"):
        st.info("Grant window reset to next available reapply date.")
    if st.button("📦 Unlock Court 2 for Resale"):
        st.success("Court 2 now re-listed in sponsorship inventory.")
