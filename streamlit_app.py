import inspect
from importlib import import_module
from itertools import dropwhile
from pathlib import Path
from typing import Callable, List

import streamlit_patches as st
from components import stoggle


def get_function_body(func):
    source_lines = inspect.getsourcelines(func)[0]
    source_lines = dropwhile(lambda x: x.startswith("@"), source_lines)
    line = next(source_lines).strip()
    if not line.startswith("def "):
        return line.rsplit(":")[-1].strip()
    elif not line.endswith(":"):
        for line in source_lines:
            line = line.strip()
            if line.endswith(":"):
                break
    # Handle functions that are not one-liners
    first_line = next(source_lines)
    # Find the indentation of the first line
    indentation = len(first_line) - len(first_line.lstrip())
    return "".join(
        [first_line[indentation:]]
        + [line[indentation:] for line in source_lines]
    )


def home():
    st.title("🪢 Streamlit Crafts Hub")
    st.write(
        """
Want to give a special touch to your [Streamlit](https://www.streamlit.io) apps?

In this hub, we feature creative usages of Streamlit we call _crafts_! Go ahead and
discover them!
"""
    )

    stoggle.main.stoggle(
        "Crafts & Streamlit Components? 🤔",
        """Crafts are useful pieces of code which are built upon Streamlit and simple Python
or HTML/JS without requiring an additional server. If you've heard of Streamlit
Components <a href="https://blog.streamlit.io/introducing-streamlit-components/">[launch blog]</a>
before, this might sound familiar! Crafts are indeed a certain
category within Streamlit Components also known as as <strong>static</strong> components. We thought
it would be useful to give them a hub considering they're much easier to build and share!""",
    )

    stoggle.main.stoggle(
        "Wait, how can I use these crafts in my app ?! 🤩",
        """It's so easy! Either copy paste the original code which is given for each craft in the
        "Source code" section, or if you want them all at once, simply install `stx` library using
        <code>pip install stx</code> and then call the crafts you like e.g. <pre><code>import stx
stx.crafts.stoggle()
</code></pre>
        to use the exact <a href="Toggle button">Toggle</a> component we are using here.
    """,
    )


def contribute():
    st.title("🙋 Contribute")
    st.write(
        """
Head over to our public [repository](https://github.com/arnaudmiribel/st-hub) and:
- Create an empty directory for your craft in the `crafts/` directory
- Add useful files for your craft in there! We usually put everything in a `main.py`
- Add a `__init__.py` file to give in some metadata so we can automatically showcase your craft in the hub! Here's an example:

```
# __init__.py
from . import main

__func__ = main.dataframe_explorer  # main function of your craft!
__title__ = "Dataframe explorer UI"  # title of your craft!
__desc__ = "Let your viewers explore dataframes themselves!"  # description of your craft!
__icon__ = "🔭"  # give your craft an icon!
__examples__ = [main.example]  # create some examples to show how cool your craft is!

```
- Submit a PR!


If you are having troubles, reach out to discuss.streamlit.io and we can help you do it!
"""
    )


def waiting_list():
    st.write(
        """
Here is a list of crafts we want to add in here:
- https://github.com/randyzwitch/streamlit-embedcode/blob/master/streamlit_embedcode/__init__.py
- https://github.com/explosion/spacy-streamlit/blob/master/spacy_streamlit/__init__.py
- https://github.com/tvst/plost
- https://github.com/tvst/st-annotated-text
- Gist static component from https://blog.streamlit.io/introducing-streamlit-components/
- Chart explorer from https://release-1-12-0.streamlitapp.com/#chart-builder
- Keyboard trigger from https://github.com/streamlit/corp/blob/main/dashboard_utils/widgets.py#L71
- Button style css from https://github.com/streamlit/data_sources_app/blob/main/utils/ui.py#L29-L51
- Johannes gui (palette, colored header) https://github.com/streamlit/corp/blob/main/dashboard_utils/gui.py
- Shap https://github.com/snehankekre/streamlit-shap
- pyLDAvis https://discuss.streamlit.io/t/showing-a-pyldavis-html/1296
- Triage those that don't have `frontend/` in https://discuss.streamlit.io/t/streamlit-components-community-tracker/4634
    """
    )


st.page(home, "Home", "🪢")
st.page(contribute, "Contribute", "🙋")


def empty():
    pass


def get_empty():
    return empty()


st.page(get_empty, "  ", " ")

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
                st.code(get_function_body(example))
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

st.page(
    waiting_list,
    "Soon... ⌛",
    " ",
)
