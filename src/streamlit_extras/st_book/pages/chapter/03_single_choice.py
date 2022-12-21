import streamlit as st
import streamlit_book as stb

st.write("A single choice question")

stb.single_choice(
    "What is the current streamlit_book version?",  # required
    ["0.4.0", "0.5.0", "0.7.0"],  # required
    2,  # required
)
