# 🚀 Setting Up Your Streamlit Extra 🚀

In this guide, you'll learn how to set up a Streamlit Extra, either for a new function or an existing one. Streamlit Extras are a great way to extend the functionality of Streamlit and share your work with the community. Let's get started! 🌟

## For a New Function (Not Yet on PyPi) ✨

1. Create an empty directory for your extra in the `src/streamlit_extras` directory. 📂

2. Add a `__init__.py` file to provide metadata for showcasing your extra in the Streamlit Hub. 📝

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

To test it out, run pip install -e . in the streamlit-extras directory, and then run the gallery/streamlit_app.py app. 🧪

## For an Existing Function (Already on GitHub and PyPi) 🌐
Create an empty directory for your extra in the src/streamlit_extras directory. 📂

Add a __init__.py file and import your main function from your package. 📝

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

1. Add your package to the list of dependencies in pyproject.toml. 📦

2. (Optional) You can add a "featured-extra" badge to your original README.md if you like! 🌟

3. To check that your package has all the required fields, run `poetry run pytest` from the repository. 🧾

4. Set up linting to standardize your code by running `pre-commit install`, which will then check the formatting of the files you added. 🛠️

5. Submit a PR and share your Streamlit Extra with the world! 🎉 👍


If you are having troubles, create an issue on the repo or [DM me on Twitter](https://twitter.com/arnaudmiribel)!


