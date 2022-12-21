import streamlit as st
import streamlit_book as stb

st.markdown(
    """
This is a **python file** that gets rendered using `streamlit_book`,
providing examples for the python functions to create certain types of activities.
"""
)

st.markdown("---")
st.markdown("A true-or-false question")
stb.true_or_false(
    'Is "Indiana Jones and the Last Crusade" the best movie of the trilogy?',
    True,
    success="You have chosen wisely",
    error="You have chosen poorly",
    button="You must choose",
)


st.markdown("---")
st.markdown("Social media buttons")
stb.share(
    "Demo of streamlit_book v0.7.0",
    "https://share.streamlit.io/sebastiandres/stb_demo_v070/main",
)
