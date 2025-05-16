import streamlit as st

def run():
    st.title("🏷️ Sponsorship Inventory Manager")

    st.markdown("### Select a Sponsorship Asset Type:")
    asset_type = st.selectbox("Asset", [
        "Dome Exterior",
        "Full Turf Naming",
        "Half Turf",
        "Turf Corner 1", "Turf Corner 2", "Turf Corner 3", "Turf Corner 4",
        "Court 1", "Court 2", "Court 3", "Court 4",
        "Banners", "Light Poles", "Attached Building", "Trails", "Pavilion",
        "Batting Cages", "Weight Room", "Track / Walking Loop",
        "Scoreboards", "Referee Uniform Sponsor",
        "Tournament Title Sponsor", "League Sponsor",
        "School or Team Package", "In-Kind Partner"
    ])

    term = st.selectbox("Term Length", ["3 Months", "6 Months", "12 Months", "Custom"])
    cash_value = st.slider("Estimated Value ($)", 500, 100000, 10000, step=500)

    st.success(f"Suggested deal: {asset_type} sponsorship at ${cash_value:,} for {term}")
    st.info("📄 Add to sponsorship proposal builder or flag as reserved.")