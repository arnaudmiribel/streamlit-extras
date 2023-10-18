import itertools
import pkgutil
from importlib import import_module

import streamlit as st
import streamlit_extras
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row

st.set_page_config(layout="centered")

""" # :knot: streamlit-extras """


@st.cache_resource
def show_extras():
    extra_names = [
        extra.name for extra in pkgutil.iter_modules(streamlit_extras.__path__)
    ]
    num_columns = 12
    columns = [
        st.columns(num_columns) for _ in range(len(extra_names) // num_columns + 1)
    ]
    columns = itertools.chain.from_iterable(columns)

    for extra_name in extra_names:
        mod = import_module(f"streamlit_extras.{extra_name}")
        icon = mod.__icon__
        next(columns).markdown("### " + icon)

    next(columns).markdown("### ...")


st.markdown(
    "streamlit-extras is a Python library putting together useful Streamlit bits of code. It"
    " includes > 20 (count emojis below!) functional or visual additions to Streamlit that will"
    " make your life easier or your apps nicer. We call them *extras* and anyone's welcome to add"
    " their owns."
)

show_extras()
add_vertical_space(1)
st.markdown("#### Learn more")
links_row = row(2, vertical_align="center")
links_row.link_button(
    "📖  Visit our documentation",
    "https://arnaudmiribel.github.io/streamlit-extras/",
    use_container_width=True,
)
links_row.link_button(
    "🐙  Visit our repository",
    "https://github.com/arnaudmiribel/streamlit-extras",
    use_container_width=True,
)
