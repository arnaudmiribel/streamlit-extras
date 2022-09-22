import inspect
import random
from importlib import import_module
from itertools import cycle, dropwhile
from pathlib import Path
from typing import Callable, List, Optional

import streamlit_patches as st

from streamlit_extras.badges import badge
from streamlit_extras.function_explorer import function_explorer
from streamlit_extras.switch_page_button import switch_page


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
        [first_line[indentation:]] + [line[indentation:] for line in source_lines]
    )


def home():
    st.title("🪢 streamlit-extras gallery")
    st.write(
        """
Welcome to the **🪢 streamlit-extras** gallery! If you want to give a special touch to your Streamlit apps, you're at the right place!

Go ahead and browse available extras in the left handside menu, and if you like them, remember, you're just a pip install away from using them:

```
pip install streamlit-extras
```

Learn more about the library on [GitHub](https://www.github.com/arnaudmiribel/streamlit-extras)!
"""
    )

    random_extra = st.button("👀 Show me a random extra now!")

    if random_extra:
        switch_page(
            random.choice(
                [
                    "Toggle button",
                    "Dataframe explorer UI",
                    "App logo",
                    "To-do items",
                    "Annotated text",
                ]
            )
        )


def contribute():
    st.title("🙋 Contribute")
    st.write(
        """
Head over to our public [repository](https://github.com/arnaudmiribel/streamlit-extras) and:
- Create an empty directory for your extra in the `extras/` directory
- Add a `__init__.py` file to give in some metadata so we can automatically showcase your extra in the hub! Here's an example:

```
# __init__.py

def my_main_function():
    pass

def example():
    pass

__func__ = my_main_function  # main function of your extra!
__title__ = "Great title!"  # title of your extra!
__desc__ = "Great description"  # description of your extra!
__icon__ = "🔭"  # give your extra an icon!
__examples__ = [example]  # create some examples to show how cool your extra is!
__author__ = "Eva Jensen"
__github_repo__ = "evajensen/my-repo"
__streamlit_cloud_url__ = "http://my-super-app.streamlitapp.com"
__pypi_name__ = ...
__experimental_playground__ = False

```
- Submit a PR!


If you are having troubles, create an issue on the repo or [DM me on Twitter](https://twitter.com/arnaudmiribel)!
"""
    )


def waiting_list():
    st.write(
        """
Here is a list of extras we want to add in here:
- ✅ https://github.com/randyzwitch/streamlit-embedcode/blob/master/streamlit_embedcode/__init__.py
- https://github.com/explosion/spacy-streamlit/blob/master/spacy_streamlit/__init__.py
- ❌ [too many functions!] https://github.com/tvst/plost
- ✅ https://github.com/tvst/st-annotated-text
- ✅ Gist static component from https://blog.streamlit.io/introducing-streamlit-components/
- Chart explorer from https://release-1-12-0.streamlitapp.com/#chart-builder
- ✅ Keyboard trigger from https://github.com/streamlit/corp/blob/main/dashboard_utils/widgets.py#L71
- ✅ Button style css from https://github.com/streamlit/data_sources_app/blob/main/utils/ui.py#L29-L51
- ✅ Johannes gui (palette, colored header) https://github.com/streamlit/corp/blob/main/dashboard_utils/gui.py
- Shap https://github.com/snehankekre/streamlit-shap
- pyLDAvis https://discuss.streamlit.io/t/showing-a-pyldavis-html/1296
- Triage those that don't have `frontend/` in https://discuss.streamlit.io/t/streamlit-components-community-tracker/4634
- DF to grid https://github.com/streamlit/app-frontpage/blob/main/utils/ui.py#L263-L264
- ✅ Top left logo from Zachary
- ✅ Button that changes page in MPA from Zachary
- Bar chart race https://github.com/streamlit/corp/blob/e22ec94bc18a46504f3053853af220cea2a97dd6/tools/parse_requirements_script.py#L79-L103
- https://github.com/sebastiandres/streamlit_book
    """
    )


st.page(home, "Home", "🪢")
st.page(contribute, "Contribute", "🙋")


def empty():
    pass


def get_empty():
    return empty()


st.page(get_empty, "  ", " ")

PATH_TO_EXTRAS = "streamlit_extras"
extra_names = [
    folder.name
    for folder in Path(PATH_TO_EXTRAS).glob("*")
    if folder.is_dir() and folder.name != "__pycache__"
]


def get_page_content(
    extra_name: str,
    icon: str,
    title: str,
    examples: List[Callable],
    func: Callable,
    inputs: dict,
    desc: str,
    author: str,
    github_repo: Optional[str] = None,
    streamlit_cloud_url: Optional[str] = None,
    pypi_name: Optional[str] = None,
    package_name: Optional[str] = None,
    twitter_username: Optional[str] = None,
    buymeacoffee_username: Optional[str] = None,
    experimental_playground: bool = False,
) -> Callable:
    def page_content():
        st.title(icon + " " + title)

        if author:
            st.caption(f"By: {author}")

        st.write(desc)

        # Social badges
        if any(
            [
                github_repo,
                streamlit_cloud_url,
                pypi_name,
                twitter_username,
                buymeacoffee_username,
            ]
        ):
            columns = cycle(st.columns(6))
            if github_repo:
                with next(columns):
                    badge("github", name=github_repo)
            if pypi_name:
                with next(columns):
                    badge("pypi", name=pypi_name)
            if streamlit_cloud_url:
                with next(columns):
                    badge("streamlit", url=streamlit_cloud_url)
            if twitter_username:
                with next(columns):
                    badge("twitter", name=twitter_username)
            if buymeacoffee_username:
                with next(columns):
                    badge("buymeacoffee", name=buymeacoffee_username)

        st.write("## Usage")

        if pypi_name:
            st.write(
                f"""
                    Automatically installed when you install `streamlit-extras`, but
                    you can also install it separately with
                    ```
                    pip install {pypi_name}
                    ```
                    """
            )

        for example in examples:
            if pypi_name:
                import_code = f"from {package_name} import {func.__name__}\n\n"
            else:
                import_code = (
                    f"from streamlit_extras.{extra_name} import" f" {func.__name__}\n\n"
                )
            st.caption(f"↓ {example.__name__} · Input code")
            st.code(import_code + get_function_body(example))
            st.caption(f"↓ {example.__name__} · Output")
            example(**inputs)

        st.write("")
        st.write("## Docstring")
        st.help(func)

        with st.expander("Show me the full code!"):
            st.code(inspect.getsource(func))

        if experimental_playground:
            st.write("")
            st.write("## Playground 🛝 [experimental]")
            st.caption("In this section, you can test the function live!")
            function_explorer(func=func)

    page_content.__name__ = title

    return page_content


settings = dict()

for extra_name in extra_names:
    mod = import_module(f"{PATH_TO_EXTRAS}.{extra_name}")
    title = mod.__title__
    icon = mod.__icon__
    func = mod.__func__
    examples = mod.__examples__
    inputs = getattr(mod, "__inputs__", dict())
    desc = mod.__desc__
    author = mod.__author__
    github_repo = getattr(mod, "__github_repo__", None)
    streamlit_cloud_url = getattr(mod, "__streamlit_cloud_url__", None)
    pypi_name = getattr(mod, "__pypi_name__", None)
    package_name = getattr(mod, "__package_name__", None)
    twitter_username = getattr(mod, "__twitter_username__", None)
    buymeacoffee_username = getattr(mod, "__buymeacoffee_username__", None)
    experimental_playground = getattr(mod, "__experimental_playground__", False)

    settings[extra_name] = dict(
        path=get_page_content(
            extra_name=extra_name,
            icon=icon,
            title=title,
            examples=examples,
            func=func,
            inputs=inputs,
            desc=desc,
            author=author,
            github_repo=github_repo,
            streamlit_cloud_url=streamlit_cloud_url,
            pypi_name=pypi_name,
            package_name=package_name,
            twitter_username=twitter_username,
            buymeacoffee_username=buymeacoffee_username,
            experimental_playground=experimental_playground,
        ),
        name=title,
        icon=icon,
    )

    st.page(**settings[extra_name])


st.page(
    waiting_list,
    "Soon... ⌛",
    " ",
)
