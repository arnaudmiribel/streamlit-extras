import streamlit as st
import streamlit_book as stb

st.write("A simple to-do list")

stb.to_do_list(
    tasks={"a": True, "b": False, "c": False},  # mandatory
    header="Description 02",  # optional
    success="Bravo!",  # optional
)
