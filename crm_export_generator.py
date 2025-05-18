
import streamlit as st
import pandas as pd

def run():
    st.title("📇 CRM Export Builder")

    data = pd.DataFrame({
        "Name": ["Jordan Smith", "Dana Lopez", "Taylor Kim"],
        "Amount": [1000, 250, 500],
        "Category": ["Adaptive", "Scholarship", "Facility"],
        "Recurring": ["No", "Yes", "No"]
    })

    st.dataframe(data)
    csv = data.to_csv(index=False)
    st.download_button("Download CSV for CRM", csv, "donors_export.csv")
