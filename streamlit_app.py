import inspect
import time
from glob import glob
from importlib import import_module

import streamlit_patches as st


def home():
    st.title("🌍 Streamlit Hub!")
    st.write(
        """
Welcome to the Streamlit Hub.

Here, you will find fun Streamlit re-usable pieces of code to customize your apps. Have fun!
"""
    )


def contribute():
    st.title("🙋 Contribute")


st.page(home, "Home", "🌎")
st.page(contribute, "Contribute", "🙋")


def empty():
    pass


st.page(empty, "―――――――――――――――――", " ")

components_names = [
    path.split("/")[-2]
    for path in glob("./components/*/")
    if "__pycache__" not in path
]

settings = dict()

for component in components_names:
    mod = import_module(f"components.{component}")
    title = mod.__title__
    icon = mod.__icon__
    func = mod.__func__
    examples = mod.__examples__

    def page_content():
        st.title(icon + " " + title)
        st.write("## Example")

        for example in examples:
            st.code(inspect.getsource(example))
            example()

        st.write("## Docstring")
        st.help(func)

        st.write("## Source code")
        st.code(inspect.getsource(func))

    # Making sure the page function has a different name so it doesn't get cached
    page_content.__name__ = title

    settings[component] = dict(
        path=page_content,
        name=title,
        icon=icon,
    )

    st.page(**settings[component])
