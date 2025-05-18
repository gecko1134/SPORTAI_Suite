
import streamlit as st
import datetime

def run():
    st.title("🌲 Trail Access + Activity Planner")

    st.markdown("### Surface Conditions & Access Today")
    today = datetime.date.today()
    st.write(f"📅 {today.strftime('%A, %B %d, %Y')}")

    st.metric("Bike Trail Status", "Open")
    st.metric("Hiking Trail", "Good")
    st.metric("Snowmobile Route", "Groomed")
    st.metric("ATV Loop", "Soft, open to limited access")

    st.markdown("### Suggested Uses")
    st.info("🟢 Promote guided hike Sat @ 10am")
    st.warning("🟠 ATV path wet in areas — post caution signage")
    st.success("🟢 Snowmobile loop cleared — alert tourism office")
