import streamlit as st

from .. import extra


@extra
def add_vertical_space(num_lines: int = 1):
    """Add vertical space to your Streamlit app."""
    for _ in range(num_lines):
        st.write("")


def example():
    add_n_lines = st.slider("Add n vertical lines below this", 1, 20, 5)
    add_vertical_space(add_n_lines)
    st.write("Here is text after the nth line!")


__title__ = "Add Vertical Space"  # title of your extra!
__desc__ = "Add n lines of vertical space to your Streamlit app in one command"  # description of your extra!
__icon__ = "👽"  # give your extra an icon!
__examples__ = [example]  # create some examples to show how cool your extra is!
__author__ = "Tyler Richards"
__experimental_playground__ = False  # Optional
