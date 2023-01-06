import streamlit as st
import streamlit_book as stb

st.write("A multiple choice question")

stb.multiple_choice(
    "I typically ask recruiters to point out which of these are a pokemon",
    {
        "ditto": True,
        "jupyter": False,
        "pyspark": False,
        "scikit": False,
        "metapod": True,
        "vulpix": True,
    },
    success="Are you a pokemon master?",
    error="Gotta catch them all!",
    button="Check",
)
