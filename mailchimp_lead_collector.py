
import streamlit as st
import requests

def run():
    st.title("📬 Mailchimp Lead Collector")

    st.markdown("Add sponsors, donors, or event leads directly to your Mailchimp list.")

    email = st.text_input("Email Address")
    category = st.selectbox("Interest Category", ["Sponsor", "Donor", "Vendor", "Volunteer", "Board Lead"])
    mc_api = st.text_input("Mailchimp API Key", type="password")
    mc_list_id = st.text_input("Audience List ID")
    mc_dc = st.text_input("Data Center (e.g., us14)")

    if st.button("Add to Mailchimp"):
        url = f"https://{mc_dc}.api.mailchimp.com/3.0/lists/{mc_list_id}/members"
        payload = {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {
                "FNAME": category
            }
        }
        headers = {
            "Authorization": f"apikey {mc_api}"
        }
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 200 or r.status_code == 204:
                st.success("✅ Added to Mailchimp!")
            else:
                st.error(f"Failed: {r.status_code} — {r.text}")
        except Exception as e:
            st.error(f"Error: {e}")
