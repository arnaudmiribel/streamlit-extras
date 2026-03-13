import pkgutil
from importlib import import_module
from typing import TypedDict

import streamlit as st

import streamlit_extras


class ExtraInfo(TypedDict):
    icon: str
    title: str
    desc: str
    author: str
    deprecated: bool


st.set_page_config(layout="centered", page_icon=":knot:", page_title="streamlit-extras")

""" # :knot: streamlit-extras """


@st.cache_resource
def get_extras_info() -> dict[str, ExtraInfo]:
    """Load all extras and their metadata.

    Returns:
        A dictionary mapping extra names to their metadata.
    """
    extras: dict[str, ExtraInfo] = {}
    for extra in pkgutil.iter_modules(streamlit_extras.__path__):
        if extra.ispkg:
            try:
                mod = import_module(f"streamlit_extras.{extra.name}")
                extras[extra.name] = {
                    "icon": getattr(mod, "__icon__", "📦"),
                    "title": getattr(mod, "__title__", extra.name),
                    "desc": getattr(mod, "__desc__", ""),
                    "author": getattr(mod, "__author__", "Unknown"),
                    "deprecated": getattr(mod, "__deprecated__", False),
                }
            except Exception:
                pass
    return extras


def show_extras_icons(extras: dict[str, ExtraInfo]) -> None:
    """Display icon buttons for all extras."""
    extra_items = list(extras.items())
    # Display in rows of 10
    for i in range(0, len(extra_items), 10):
        batch = extra_items[i : i + 10]
        cols = st.columns(len(batch))
        for col, (extra_name, info) in zip(cols, batch, strict=False):
            col.link_button(
                info["icon"],
                f"https://arnaudmiribel.github.io/streamlit-extras/extras/{extra_name}/",
                help=info["title"],
                width="stretch",
            )


st.markdown(
    "streamlit-extras is a Python library putting together useful Streamlit bits of code. It"
    " includes > 40 (count emojis below!) functional or visual additions to Streamlit that will"
    " make your life easier or your apps nicer. We call them *extras* and anyone's welcome to add"
    " their owns!"
)

st.space(1)

extras = get_extras_info()
show_extras_icons(extras)

st.space(1)
st.markdown(
    """
#### Get started
```
pip install streamlit-extras
```
"""
)

st.space(1)
st.markdown("#### Learn more")
col1, col2 = st.columns(2)
col1.link_button(
    "📖  Visit our documentation",
    "https://arnaudmiribel.github.io/streamlit-extras/",
    width="stretch",
)
col2.link_button(
    "🐙  Visit our repository",
    "https://github.com/arnaudmiribel/streamlit-extras",
    width="stretch",
)

# Explorer section
st.space(2)
st.markdown("#### Explore extras")

# Build options for selectbox with icons and titles
extra_options = {name: f"{info['icon']} {info['title']}" for name, info in extras.items()}

selected_extra = st.selectbox(
    "Select an extra to explore",
    options=list(extra_options.keys()),
    format_func=lambda x: extra_options[x],
    index=None,
    placeholder="Choose an extra...",
)

if selected_extra:
    info = extras[selected_extra]
    mod = import_module(f"streamlit_extras.{selected_extra}")

    # Show metadata
    st.markdown(f"### {info['icon']} {info['title']}")

    if info["deprecated"]:
        st.warning("This extra is deprecated.")

    if info["desc"]:
        st.markdown(info["desc"])

    st.caption(f"Author: {info['author']}")

    # Run examples
    examples = getattr(mod, "__examples__", [])
    if examples:
        st.markdown("**Example:**")
        for example_func in examples:
            try:
                with st.container(border=True):
                    example_func()
            except Exception as e:
                st.error(f"Error running example: {e}")
    else:
        st.info("No examples available for this extra.")
