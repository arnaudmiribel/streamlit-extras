import pkgutil
from importlib import import_module
from typing import List

import pytest

import streamlit_extras


def get_extras() -> List[str]:
    return [
        extra.name
        for extra in pkgutil.iter_modules(streamlit_extras.__path__)
        if extra.ispkg
    ]


@pytest.mark.parametrize("extra", get_extras())
def test_extra_attributes(extra: str):
    mod = import_module(f"streamlit_extras.{extra}")
    assert isinstance(mod.__title__, str)
    assert isinstance(mod.__icon__, str)
    assert isinstance(mod.__desc__, str)
    assert hasattr(mod, "__funcs__")
    assert isinstance(mod.__funcs__, list)
    for func in mod.__funcs__:
        assert callable(func)
    # If you have multiple functions, then each example function must
    # specify which of these functions must be imported
    if len(mod.__funcs__) > 1:
        assert isinstance(mod.__examples__, dict)
    assert len(mod.__examples__) > 0
    if isinstance(mod.__examples__, dict):
        for example, funcs in mod.__examples__.items():
            assert callable(example)
            for func in funcs:
                assert callable(func)
    assert isinstance(mod.__author__, str)
    if hasattr(mod, "__inputs__"):
        assert isinstance(mod.__inputs__, dict)
    if hasattr(mod, "__github_repo__"):
        assert isinstance(mod.__github_repo__, str)
    if hasattr(mod, "__pypi_name__"):
        assert isinstance(mod.__pypi_name__, str)
        # If __pypi_name__ is set, __package_name__ should be set too
        assert isinstance(mod.__package_name__, str)
    if hasattr(mod, "__streamlit_cloud_url__"):
        assert isinstance(mod.__streamlit_cloud_url__, str)
        assert "streamlit" in mod.__streamlit_cloud_url__
    if hasattr(mod, "__twitter_username__"):
        assert isinstance(mod.__twitter_username__, str)
    if hasattr(mod, "__buymeacoffee_username__"):
        assert isinstance(mod.__buymeacoffee_username__, str)
    if hasattr(mod, "__forum_url__"):
        assert isinstance(mod.__forum_url__, str)
        assert "discuss.streamlit.io" in mod.__forum_url__
    if hasattr(mod, "__experimental_playground__"):
        assert isinstance(mod.__experimental_playground__, bool)
    if hasattr(mod, "__experimental_playground_funcs__"):
        assert isinstance(mod.__experimental_playground_funcs__, list)
        for func in mod.__experimental_playground_funcs__:
            assert callable(func)


@pytest.mark.parametrize("extra", get_extras())
def test_extra_tests(extra: str):
    mod = import_module(f"streamlit_extras.{extra}")
    if hasattr(mod, "__tests__"):
        for test in mod.__tests__:
            test()
