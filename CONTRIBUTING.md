# 🙋 Contribute

Head over to our public [repository](https://github.com/arnaudmiribel/streamlit-extras) and:

- Create an empty directory for your extra in the `src/streamlit_extras` directory
- Add a `__init__.py` file to give in some metadata so we can automatically showcase your extra in the hub!

  - If your function is new, and doesn't yet exist on PyPi, here's an example of how to add it:

    ```python
    # extras/<extra_name>/__init__.py
    from .. import extra

    @extra  # this will register your function's extra
    def my_main_function():
        ...

    def example():
        ...

    __title__ = "Great title!"  # title of your extra!
    __desc__ = "Great description"  # description of your extra!
    __icon__ = "🔭"  # give your extra an icon!
    __examples__ = [example]  # create some examples to show how cool your extra is!
    __author__ = "Eva Jensen"
    __experimental_playground__ = False # Optional
    ```
    To test it out, run `pip install -e .` in the `streamlit-extras` directory, and then run the `gallery/streamlit_app.py` app.

  - If your extra already exists on github and pypi:

    ```python
    # extras/<extra_name>/__init__.py

    from my_package import my_main_function
    from .. import extra

    my_main_function = extra(my_main_function)

    def example():
        ...

    __title__ = "Great title!"  # title of your extra!
    __desc__ = "Great description"  # description of your extra!
    __icon__ = "🔭"  # give your extra an icon!
    __examples__ = [example]  # create some examples to show how cool your extra is!
    __author__ = "Eva Jensen"
    __pypi_name__ = "my-cool-package"
    __package_name__ = "my_package"
    __github_repo__ = "evajensen/my-repo" # Optional
    __streamlit_cloud_url__ = "http://my-super-app.streamlitapp.com" # Optional
    __experimental_playground__ = False # Optional
    ```

    Then add `my_package` to the list of `dependencies` in `pyproject.toml`
  - You can also add a "featured-extra" badge to your original README.md if you like! <a href="https://github.com/arnaudmiribel/streamlit-extras"> <img src="https://img.shields.io/badge/-%F0%9F%AA%A2%20featured%20extra-e8ded1"></img></a>

- If you'd like to test that your package has all the required fields, you can run `poetry run pytest` from the repository
- You can set up linting to standardize your code by running `pre-commit install`, which will then check the formatting of the files you added
- Submit a PR!

If you are having troubles, create an issue on the repo or [DM me on Twitter](https://twitter.com/arnaudmiribel)!
