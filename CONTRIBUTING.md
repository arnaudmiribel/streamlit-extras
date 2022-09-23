# 🙋 Contribute

Head over to our public [repository](https://github.com/arnaudmiribel/streamlit-extras) and:

- Create an empty directory for your extra in the `extras/` directory
- Add a `__init__.py` file to give in some metadata so we can automatically showcase your extra in the hub!

  - If your function is new, and doesn't yet exist on PyPi, here's an example of how to add it:

    ```python
    # extras/<extra_name>/__init__.py

    def my_main_function():
        ...

    def example():
        ...

    __func__ = my_main_function  # main function of your extra!
    __title__ = "Great title!"  # title of your extra!
    __desc__ = "Great description"  # description of your extra!
    __icon__ = "🔭"  # give your extra an icon!
    __examples__ = [example]  # create some examples to show how cool your extra is!
    __author__ = "Eva Jensen"
    __experimental_playground__ = False # Optional
    ```

  - If your extra already exists on github and pypi:

    ```python
    # extras/<extra_name>/__init__.py

    from my_package import my_main_function

    def example():
        ...

    __func__ = my_main_function  # main function of your extra!
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

- If you'd like to test that your package has all the required fields, you can run `poetry run pytest` from the repository
- You can set up linting to standardize your code by running `pre-commit install`, which will then check the formatting of the files you added
- Submit a PR!

If you are having troubles, create an issue on the repo or [DM me on Twitter](https://twitter.com/arnaudmiribel)!
