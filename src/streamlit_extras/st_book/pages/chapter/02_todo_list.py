import streamlit as st
import streamlit_book as stb

st.write("A simple to-do list")

c1, c2 = st.columns([5,5])
with c1:
    stb.to_do_list( 
                tasks={"a":True, "b":False, "c":False}, # mandatory
                header="Description 02", # optional argument
                success="Bravo!" # optional argument
                )
