import inspect
import pkgutil
import textwrap
from importlib import import_module

import streamlit as st
import streamlit_extras
from stlite_sandbox import stlite_sandbox
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.row import row

st.set_page_config(layout="wide", page_icon=":knot:", page_title="streamlit-extras")


def centered():
    _, container, _ = st.columns([1, 3, 1])
    return container


with centered():
    """# :knot: streamlit-extras"""

    st.markdown(
        "streamlit-extras is a Python library putting together useful Streamlit bits of code. It"
        " includes > 40 (count emojis below!) functional or visual additions to Streamlit that will"
        " make your life easier or your apps nicer. We call them *extras* and anyone's welcome to add"
        " their owns!"
    )

    add_vertical_space(1)

    extra_names = [
        extra.name for extra in pkgutil.iter_modules(streamlit_extras.__path__)
    ]

    icon_row = row(10)
    buttons = list()
    extras = list()

    for extra_name in extra_names:
        mod = import_module(f"streamlit_extras.{extra_name}")
        icon = mod.__icon__
        buttons.append(
            icon_row.button(
                icon,
                f"https://arnaudmiribel.github.io/streamlit-extras/extras/{extra_name}/",
                help=mod.__title__,
                use_container_width=True,
            )
        )
        extras.append(mod)

    icon_row.markdown("### ...")


DEFAULT_CODE = """st.balloons()"""

if "code" not in st.session_state:
    st.session_state["code"] = DEFAULT_CODE

if "requirements" not in st.session_state:
    st.session_state["requirements"] = ["streamlit", "streamlit-extras"]

button_hit = any(buttons)

""" # Playground """

if button_hit:
    extra_name = extra_names[buttons.index(True)]
    extra = extras[extra_names.index(extra_name)]
    if extra.__stlite__:
        example = extra.__examples__[0]
        if hasattr(example, "__pypi_name__"):
            if example.__pypi_name__ not in st.session_state["requirements"]:
                st.session_state["requirements"] += [example.__pypi_name__]
        example_code = inspect.getsource(example)
        example_name = example.__name__
        st.session_state["code"] = f"from streamlit_extras.{extra_name} import *\n\n"
        st.session_state["code"] += textwrap.dedent(
            "\n".join(example_code.splitlines()[1:])
        )
    else:
        st.session_state["code"] = DEFAULT_CODE

    st.session_state["extra_name"] = extra_name
    st.session_state["extra_title"] = f"{extra.__icon__} {extra.__title__}"


if "extra_name" in st.session_state:
    extra_docs_url = f"https://arnaudmiribel.github.io/streamlit-extras/extras/{st.session_state.extra_name}/"
    st.caption(
        f"Trying out **{st.session_state.extra_title}** extra... Learn more in the [docs]({extra_docs_url})!"
    )

stlite_sandbox(
    "import streamlit as st\n\n" + st.session_state.code,
    height=800,
    editor=True,
    requirements=st.session_state.requirements,
)


with centered():
    add_vertical_space(1)
    st.markdown(
        """
    #### Get started
    ```
    pip install streamlit-extras
    ```
    """
    )

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


# import streamlit as st

# from streamlit_extras.add_vertical_space import *

# """# 👽 Add Vertical Space"""

# """**Docstring**"""
# st.help(add_vertical_space)

# """**Example**"""
# add_n_lines = st.slider("Add n vertical lines below this", 1, 20, 5)
# add_vertical_space(add_n_lines)
# st.write("Here is text after the nth line!")
