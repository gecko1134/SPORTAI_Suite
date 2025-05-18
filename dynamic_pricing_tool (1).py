
import streamlit as st

def run():
    st.title("💸 Dynamic Pricing Tool")
    st.markdown("Adjust rates based on demand, day, and time.")

    sport = st.selectbox("Sport", ["Basketball", "Soccer", "Volleyball", "Pickleball"])
    surface = st.selectbox("Surface", ["Court", "Full Turf", "Half Turf"])
    day = st.selectbox("Day Type", ["Weekday", "Weekend"])
    time = st.selectbox("Time Slot", ["Morning", "Afternoon", "Evening"])
    base_price = st.number_input("Base Hourly Price ($)", 30, 500, 100)

    multiplier = 1.2 if day == "Weekend" else 1.0
    if time == "Evening":
        multiplier += 0.3
    elif time == "Morning":
        multiplier -= 0.1

    dynamic_price = round(base_price * multiplier, 2)
    st.success(f"Suggested Price: ${dynamic_price}")
