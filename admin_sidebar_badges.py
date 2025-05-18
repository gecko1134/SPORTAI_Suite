
import streamlit as st

def run():
    st.title("🚨 Admin Sidebar Alerts Preview")

    st.markdown("This module injects real-time alert counts into the sidebar.")
    st.markdown("Use Streamlit’s experimental sidebar state or link modules with metrics.")

    st.sidebar.markdown("### 🔴 3 Critical Alerts")
    st.sidebar.markdown("### 🟡 2 Contracts Expiring")
    st.sidebar.markdown("### 🟢 System Healthy")

    st.success("✅ Sidebar badge logic previewed. Expand with real data connectors.")
