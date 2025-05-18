
import streamlit as st
import pandas as pd

def run():
    st.title("🔄 CRM Sync: Grant + Donor Submissions")

    data = pd.DataFrame({
        "Name": ["Jordan Smith", "Play60 Grant", "HealthCo Foundation"],
        "Type": ["Donor", "Grant", "Donor"],
        "Amount": [1000, 10000, 5000],
        "Purpose": ["Scholarship", "Youth Sports", "Adaptive Access"],
        "Date": ["2024-06-10", "2024-06-01", "2024-06-08"]
    })

    st.dataframe(data)

    csv = data.to_csv(index=False)
    st.download_button("📤 Export for CRM (CSV)", csv, file_name="crm_export.csv")
