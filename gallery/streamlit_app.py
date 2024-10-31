from __future__ import annotations

import inspect
import pkgutil
import textwrap
import warnings
from importlib import import_module

import streamlit as st
import streamlit_extras
from stlite_sandbox import stlite_sandbox
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_pills import pills

warnings.filterwarnings("ignore", category=DeprecationWarning)


@st.cache_resource
def get_extras_metadata() -> list:
    extras_metadata = list()
    for _extra in pkgutil.iter_modules(streamlit_extras.__path__):
        module = import_module(f"streamlit_extras.{_extra.name}")
        metadata = {
            "module": module,
            "name": _extra.name,
            "title": module.__title__,
            "icon": module.__icon__,
            "examples": module.__examples__,
            "playground": getattr(module, "__playground__", False),
        }

def show_extras():
    extra_names = [
        extra.name
        for extra in pkgutil.iter_modules(streamlit_extras.__path__)
        if extra.ispkg
    ]

    metadata["label"] = f"{metadata['icon']}  {metadata['title']}"
    extras_metadata.append(metadata)
    return extras_metadata


st.set_page_config(
    layout="wide",
    page_icon=":knot:",
    page_title="streamlit-extras",
)

extras_metadata = get_extras_metadata()


def body():
    _, container, _ = st.columns([1, 5, 1])
    return container


with body():
    """# :knot: streamlit-extras"""

    left, right = st.columns(2, gap="large")

    with left:
        st.subheader("Summary", divider=True)
        st.markdown(
            "streamlit-extras is a Python library putting together useful Streamlit bits of code. It"
            " includes > 40 (count emojis below!) functional or visual additions to Streamlit that will"
            " make your life easier or your apps nicer. "
            " We call them *extras* and anyone's welcome to add"
            " their owns!"
        )

    with right:
        st.subheader("Get started!", divider=True)
        st.code("pip install streamlit-extras")
        st.link_button(
            "📖  Visit our documentation",
            "https://arnaudmiribel.github.io/streamlit-extras/",
            use_container_width=True,
        )
        st.link_button(
            "🐙  Visit our repository",
            "https://github.com/arnaudmiribel/streamlit-extras",
            use_container_width=True,
        )

    add_vertical_space(1)
    st.subheader("Playground", divider=True)
    st.markdown(
        """Choose an extra and play with it in the playground below! Powered
                by [stlite-dynamic-sandbox](https://github.com/blackary/stlite-dynamic-sandbox),
                a Streamlit component to run [stlite](https://github.com/whitphx/stlite) in Streamlit apps!"""
    )

    with st.container(border=True):
        st.caption("Choose extra:")

        selected = pills(
            "Select an extra",
            [extra["label"] for extra in extras_metadata],
            label_visibility="collapsed",
        )


DEFAULT_CODE = """st.balloons()"""
EXTRA_DOCS_URL = ""
FALLBACK_CODE = '''st.warning("""Can't use the playground with **{extra_label}**
extra unfortunately. But you should go and visit its
[documentation](https://arnaudmiribel.github.io/streamlit-extras/extras/{extra_name}/)
to learn more about it!
""")
'''

if "code" not in st.session_state:
    st.session_state["code"] = DEFAULT_CODE

if "requirements" not in st.session_state:
    st.session_state["requirements"] = ["streamlit", "streamlit-extras"]


matching_extras: list[dict] = [x for x in extras_metadata if x["label"] == selected]
if len(matching_extras) > 0:
    extra: dict = matching_extras[0]

if extra["playground"]:

    # Get the first extra example metadata
    if isinstance(extra["examples"], list):
        example = extra["examples"][0]
    elif isinstance(extra["examples"], dict):
        example = extra["examples"][list(extra["examples"].keys())[0]][0]

    example_code = inspect.getsource(example)
    example_name = example.__name__

    # If extra is a PyPI package, then add it to the requirements.txt
    if hasattr(example, "__pypi_name__"):
        if example.__pypi_name__ not in st.session_state["requirements"]:
            st.session_state["requirements"] += [example.__pypi_name__]

    st.session_state["code"] = f"from streamlit_extras.{extra['name']} import *\n\n"
    st.session_state["code"] += textwrap.dedent(
        "\n".join(example_code.splitlines()[1:])
    )

else:
    st.session_state["code"] = FALLBACK_CODE.format(
        extra_label=extra["label"], extra_name=extra["name"]
    )

st.session_state["extra_name"] = extra["name"]
st.session_state["extra_title"] = extra["label"]

with body():

    if "extra_name" in st.session_state:
        extra_docs_url = f"https://arnaudmiribel.github.io/streamlit-extras/extras/{st.session_state.extra_name}/"

    PREFIX_CODE = """import streamlit as st

"""

    stlite_sandbox(
        PREFIX_CODE + st.session_state.code,
        height=400,
        editor=True,
        requirements=st.session_state.requirements,
        scrollable=True,
    )
