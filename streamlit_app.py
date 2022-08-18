import inspect
import typing
from importlib import import_module
from pathlib import Path
from typing import Callable, List

import streamlit_patches as st


def home():
    st.title("🪢 Streamlit Crafts Hub")
    st.write(
        """
Want to give a special touch to your [Streamlit](https://www.streamlit.io) app? In 
this hub, we feature creative usages of Streamlit! Browse them, use them 
and if you feel like sharing your special crafts, head over to the 🙋 **Contribute** page!
"""
    )
    
    st.caption(
        """
Crafts are Streamlit Components that do not require JS.
"""
    )
    
    


def contribute():
    st.title("🙋 Contribute")
    st.write(
        """
Head over to our public [repository](https://github.com/arnaudmiribel/st-hub) and:
- Create an empty directory for your craft in the `crafts/` directory
- Add useful files for your craft in there! We usually put everything in a `main.py`
- Add a `__init__.py` file to give in some metadata so we can automatically feature 
your craft in the hub! Here's an example

```
# __init__.py
from . import main

__func__ = main.dataframe_explorer  # main function of your craft!
__title__ = "Dataframe explorer UI"  # title of your craft!
__desc__ = "Let your viewers explore dataframes themselves!"  # description of your craft!
__icon__ = "🔭"  # give your craft an icon!
__examples__ = [main.example]  # create some examples to show how cool your craft is!

```
"""
    )
        
st.page(home, "Home", "🪢")
st.page(contribute, "Contribute", "🙋")


def empty():
    pass


st.page(empty, "―――――――――――――――――", " ")

component_names = [folder.name for folder in Path("components").glob("*")]

settings = dict()

for component in component_names:
    mod = import_module(f"components.{component}")
    title = mod.__title__
    icon = mod.__icon__
    func = mod.__func__
    examples = mod.__examples__
    if hasattr(mod, "__inputs__"):
        inputs = mod.__inputs__
    else:
        inputs = dict()

    def get_page_content(
        icon: str,
        title: str,
        examples: List[Callable],
        func: Callable,
        inputs: dict,
    ) -> Callable:
        def page_content():
            st.title(icon + " " + title)
            st.write("## Example")

            for example in examples:
                st.code(inspect.getsource(example))
                example(**inputs)

            st.write("")
            st.write("## Docstring")
            st.help(func)

            st.write("## Source code")
            st.code(inspect.getsource(func))

        page_content.__name__ = title

        return page_content

    settings[component] = dict(
        path=get_page_content(icon, title, examples, func, inputs),
        name=title,
        icon=icon,
    )

    st.page(**settings[component])
