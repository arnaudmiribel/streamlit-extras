import streamlit as st
from streamlit.components.v1 import html

# Replace this with your actual Stripe publishable key
stripe_publishable_key = "your_stripe_publishable_key"

# Set page title and icon
st.set_page_config(page_title="Streamlit Extras - Stripe Payments", page_icon="💳")

# Header
st.title("Streamlit Extras - Stripe Payments")

# Terms and conditions
st.info("This is a sample terms and conditions text. Lorem ipsum dolor sit amet...")

terms_state = st.checkbox("I agree to the Terms and Conditions")

# Payment section
if terms_state:
    st.write("Thanks for confirming the terms and conditions!")
    st.title("💰 Payment")
    st.write("To complete your booking, please make the payment.")
    stripe_js = f"""
    <script async src="https://js.stripe.com/v3/buy-button.js"></script>
    <stripe-buy-button
      buy-button-id="buy_btn_1NKjSSBY7L5WREAJ0wKVXsQB"
      publishable-key="{stripe_publishable_key}"
    ></stripe-buy-button>
    """.format(stripe_publishable_key)
    st.html(stripe_js) 
    st.image("stripe_qr_download.png", caption="Scan the QR code to pay")
