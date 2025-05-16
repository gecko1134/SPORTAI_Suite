import streamlit as st
import pandas as pd

def run():
    st.title("📈 Real-Time Revenue Pro Forma")

    categories = ["Memberships", "Sponsorships", "Rentals", "Food Sales", "Events"]
    amounts = [12000, 75000, 30000, 8000, 15000]

    df = pd.DataFrame({"Category": categories, "Monthly Revenue ($)": amounts})
    df["Annualized ($)"] = df["Monthly Revenue ($)"] * 12
    st.dataframe(df)

    st.metric("📊 Total Projected Annual Revenue", f"${df['Annualized ($)'].sum():,.0f}")