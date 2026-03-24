import inspect
import pkgutil
import textwrap
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


st.set_page_config(layout="wide", page_icon=":material/extension:", page_title="streamlit-extras")

with st.container(horizontal=True, vertical_alignment="bottom"):
    st.markdown("# :material/extension: streamlit-extras", width="content")
    with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
        st.link_button(
            "GitHub",
            "https://arnaudmiribel.github.io/streamlit-extras/",
            width="content",
            icon=":material/code_blocks:",
        )
        st.link_button(
            "Documentation",
            "https://arnaudmiribel.github.io/streamlit-extras/",
            width="content",
            icon=":material/book_2:",
            type="primary",
        )


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


"""A library to add some extra touches to your Streamlit apps. Get started easily:"""

with st.container(horizontal=True, vertical_alignment="center"):
    st.code("pip install streamlit-extras", width="content")
    st.space("small")
    st.markdown("Or use uv", width="content")
    st.code("uv add streamlit-extras", width="content")

"""Play with the demos below to discover some extras."""

extras = get_extras_info()
extras_unsuited_to_demos = {
    "bottom_container",  # Out of context
    "concurrency_limiter",  # Nothing visual
    "floating_button",  # Out of context
    "great_tables",  # Requires extra package
    "jupyterlite",  # Doesn't look great
    "customize_running",  # Content overlaps
}

extra_options = {
    name: f"{info['icon']} {info['title']}"
    for name, info in extras.items()
    if not info["deprecated"] and name not in extras_unsuited_to_demos
}

left, right = st.columns((2.5, 3))

with left.expander("**Choose extra**", expanded=True, icon=":material/extension:"):
    selected_extra = st.pills(
        "Select extra for a demo",
        options=list(extra_options.keys()),
        format_func=lambda x: extra_options[x],
        label_visibility="collapsed",
        bind="query-params",
        key="extra",
        default="radial_menu",
    )

if selected_extra is None:
    right.markdown("Choose an extra first.")
    st.stop()

assert selected_extra is not None  # for type checker (st.stop() doesn't return)

with right:
    info = extras[selected_extra]
    mod = import_module(f"streamlit_extras.{selected_extra}")

    # Show metadata
    with st.expander(
        f"**{info['title']}** demo by :material/person: {info['author']}", expanded=True, icon=info["icon"]
    ):
        if info["desc"]:
            st.markdown(info["desc"])

        # Run examples
        examples = getattr(mod, "__examples__", [])
        if examples:
            if len(examples) > 1:
                example_func = st.selectbox("Choose example", examples, format_func=lambda f: f.__name__)
            else:
                example_func = next(iter(examples))
            try:
                with st.expander("Example code"):
                    function_code = inspect.getsource(example_func)

                    # Drop function wrapper in function code
                    function_code = textwrap.dedent("\n".join(function_code.splitlines()[1:]))
                    code = f"from streamlit_extras.{selected_extra} import *\n\n{function_code}"
                    st.code(code, language="python")
                with st.expander("Example output", expanded=True):
                    example_func()
            except Exception as e:
                st.error(f"Error running example: {e}")
        else:
            st.info("No examples available for this extra.")
