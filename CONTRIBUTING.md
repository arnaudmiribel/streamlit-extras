# Contributing your own extra

In this guide, you'll learn how to publish a new Streamlit extra, either from a new function or an existing package. Let's get started!

## Requirements

Set up linting to standardize your code by running `pre-commit install`, which will then check the formatting of the files you added.

## Case 1: From a new function (not yet on PyPi)

1. Create an empty directory for your extra in the `src/streamlit_extras` directory.

2. Add a `__init__.py` file to provide metadata that will appear in our docs.

```python
# extras/<extra_name>/__init__.py
from .. import extra

@extra  # this will register your function's extra
def my_main_function():
    ...

def example():
    ...

__title__ = "Great title!"  # title of your extra! 🏆
__desc__ = "Great description"  # description of your extra! 💡
__icon__ = "🔭"  # give your extra an icon! 🌠
__examples__ = [example]  # create some examples to show how cool your extra is! 🚀
__author__ = "Eva Jensen"
__experimental_playground__ = False  # Optional

```

3. To test it out, run `uv sync --dev` in the `streamlit-extras` directory, and then `uv run streamlit run gallery/streamlit_app.py` app.

4. Submit a PR and share your extra with the world! 🎉

## Case 2: From an existing package (already in PyPi)

Create an empty directory for your extra in the src/streamlit_extras directory.

Add a __init__.py file and import your main function from your package.

```python
# extras/<extra_name>/__init__.py

from my_package import my_main_function
from .. import extra

my_main_function = extra(my_main_function)

def example():
    ...

__title__ = "Great title!"  # title of your extra! 🏆
__desc__ = "Great description"  # description of your extra! 💡
__icon__ = "🔭"  # give your extra an icon! 🌠
__examples__ = [example]  # create some examples to show how cool your extra is! 🚀
__author__ = "Eva Jensen"
__pypi_name__ = "my-cool-package"
__package_name__ = "my_package"
__github_repo__ = "evajensen/my-repo"  # Optional
__streamlit_cloud_url__ = "http://my-super-app.streamlitapp.com"  # Optional
__experimental_playground__ = False  # Optional

```

1. Add your package to the list of dependencies in pyproject.toml.

2. (Optional) You can add a "featured-extra" badge to your original README.md if you like!

3. To check that your package has all the required fields, run `uv run pytest` from the repository.

4. Submit a PR and share your extra with the world! 🎉

## Help

If you are having troubles, create an issue or [DM me on Twitter](https://twitter.com/arnaudmiribel)!


