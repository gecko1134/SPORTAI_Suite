
import streamlit as st
import pandas as pd
import plotly.express as px

def run():
    st.title("📊 CRM + Pipeline Dashboard")

    df = pd.DataFrame({
        "Deal": ["TechNow", "HealthCo", "BankCo", "Jordan Smith", "Play60 Grant"],
        "Type": ["Sponsor", "Sponsor", "Sponsor", "Donor", "Grant"],
        "Stage": ["Proposal Sent", "Negotiation", "Closed Won", "Closed Won", "Submitted"],
        "Amount": [12000, 8000, 15000, 1000, 10000]
    })

    stage_chart = px.pie(df, names="Stage", title="Deals by Funnel Stage")
    revenue_bar = px.bar(df, x="Deal", y="Amount", color="Stage", title="Deal Value by Partner")

    st.plotly_chart(stage_chart, use_container_width=True)
    st.plotly_chart(revenue_bar, use_container_width=True)

    st.metric("Total Value", f"${df['Amount'].sum():,}")
