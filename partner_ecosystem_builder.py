
import streamlit as st
import datetime
import qrcode
from io import BytesIO
from PIL import Image

def run():
    st.set_page_config(page_title="Partner Ecosystem Builder", layout="wide")

    st.title("🏗️ Partner Ecosystem Builder")
    st.markdown("Manage sponsors, tenants, zones, proposals, and estimated value.")

    tabs = st.tabs(["🔍 Target List", "🗺️ Zone Planner", "📄 Proposal Generator", 
                    "📆 Activation Calendar", "📊 Value Estimator", "🔗 Lead Capture"])

    with tabs[0]:
        st.subheader("Target Partners")
        st.text_input("Business or Organization Name")
        st.selectbox("Type", ["Restaurant", "Retail", "Clinic", "Sponsor", "Bank", "Other"])
        st.text_area("Notes or Relationship Details")
        st.button("➕ Add to Target List")

    with tabs[1]:
        st.subheader("Zone Planner")
        available_zones = ["Plaza Booth A", "Interior Banner 1", "Clinic Suite", "Retail Bay 2"]
        assigned_zones = st.multiselect("Assign Zones to Active Partner", available_zones)

    with tabs[2]:
        st.subheader("Auto Proposal Generator")
        category = st.selectbox("Select Category", ["Healthcare", "Banking", "Retail", "Restaurant", "Other"])
        duration = st.slider("Contract Duration (Months)", 1, 360, 12)
        exposure = st.selectbox("Exposure Level", ["Low", "Medium", "High"])
        st.button("📄 Generate Proposal Summary")

    with tabs[3]:
        st.subheader("Activation Calendar")
        st.date_input("Add New Activation Date")
        st.text_input("Event Name or Sponsor")
        st.button("📆 Save Date")

    with tabs[4]:
        st.subheader("Value Estimator")
        months = st.slider("Months", 1, 360, 12)
        exposure = st.select_slider("Exposure", options=["Low", "Medium", "High"])
        base_price = 1000
        multiplier = {"Low": 1, "Medium": 2, "High": 3}
        estimated_value = base_price * months * multiplier[exposure]
        st.metric("Estimated Sponsorship Value ($)", f"{estimated_value:,.2f}")

    with tabs[5]:
        st.subheader("Generate QR for Sponsor Inquiry Form")
        form_url = st.text_input("Paste Google Form or Custom Inquiry Link")
        if st.button("Generate QR Code") and form_url:
            img = qrcode.make(form_url)
            buf = BytesIO()
            img.save(buf)
            buf.seek(0)
            st.image(Image.open(buf), caption="Sponsor Inquiry QR Code", width=200)
