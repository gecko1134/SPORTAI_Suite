
import streamlit as st
import requests

def run():
    st.title("💼 HubSpot Deal Logger")

    sponsor = st.text_input("Sponsor/Company Name")
    contact_email = st.text_input("Contact Email")
    deal_value = st.number_input("Estimated Deal Value ($)", 500, 500000, 10000)
    stage = st.selectbox("Deal Stage", ["Prospecting", "Proposal Sent", "Negotiation", "Closed Won", "Closed Lost"])
    api_key = st.text_input("HubSpot API Key", type="password")

    if st.button("Log Deal to HubSpot"):
        url = "https://api.hubapi.com/crm/v3/objects/deals"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "properties": {
                "dealname": f"{sponsor} Sponsorship",
                "amount": deal_value,
                "dealstage": stage.lower().replace(" ", "_"),
                "hubspot_owner_id": "",  # Optional owner assignment
                "pipeline": "default"
            }
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                st.success("✅ Deal logged in HubSpot CRM!")
            else:
                st.error(f"HubSpot Error: {response.status_code} — {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
