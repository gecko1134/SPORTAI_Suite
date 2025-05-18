
import streamlit as st

def run():
    st.title("💳 Donation Checkout")

    st.markdown("Support our park expansion or youth access programs.")

    amount = st.selectbox("Donation Amount", [25, 50, 100, 250, 500, 1000])
    method = st.selectbox("Payment Method", ["Stripe", "PayPal"])

    st.success(f"You're donating ${amount:,} via {method}.")

    if method == "Stripe":
        st.markdown("🔗 [Pay Now via Stripe](https://buy.stripe.com/test_4gw5no3Fkgds3kUaEE)")
    elif method == "PayPal":
        st.markdown("🔗 [Donate via PayPal](https://www.paypal.com/donate/?hosted_button_id=XXXX)")

    st.info("✅ You'll receive a confirmation and thank-you message.")
