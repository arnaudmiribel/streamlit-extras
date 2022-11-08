import pkgutil
from importlib import import_module
from typing import List

import pytest

import streamlit_extras


def get_extras() -> List[str]:
    return [extra.name for extra in pkgutil.iter_modules(streamlit_extras.__path__)]


@pytest.mark.parametrize("extra", get_extras())
def test_extra_attributes(extra: str):
    mod = import_module(f"streamlit_extras.{extra}")
    assert type(mod.__title__) == str
    assert type(mod.__icon__) == str
    assert type(mod.__desc__) == str
    assert hasattr(mod, "__funcs__") or hasattr(mod, "__func__")
    if hasattr(mod, "__funcs__"):
        assert type(mod.__funcs__) == list
        for func in mod.__funcs__:
            assert callable(func)
    else:
        assert callable(mod.__func__)
    assert len(mod.__examples__) > 0
    if type(mod.__examples__) == dict:
        for example, funcs in mod.__examples__.items():
            assert callable(example)
            for func in funcs:
                assert callable(func)
    assert type(mod.__author__) == str
    if hasattr(mod, "__inputs__"):
        assert type(mod.__inputs__) == dict
    if hasattr(mod, "__github_repo__"):
        assert type(mod.__github_repo__) == str
    if hasattr(mod, "__pypi_name__"):
        assert type(mod.__pypi_name__) == str
        # If __pypi_name__ is set, __package_name__ should be set too
        assert type(mod.__package_name__) == str
    if hasattr(mod, "__streamlit_cloud_url__"):
        assert type(mod.__streamlit_cloud_url__) == str
        assert "streamlit" in mod.__streamlit_cloud_url__
    if hasattr(mod, "__twitter_username__"):
        assert type(mod.__twitter_username__) == str
    if hasattr(mod, "__buymeacoffee_username__"):
        assert type(mod.__buymeacoffee_username__) == str
    if hasattr(mod, "__forum_url__"):
        assert type(mod.__forum_url__) == str
        assert "discuss.streamlit.io" in mod.__forum_url__
    if hasattr(mod, "__experimental_playground__"):
        assert type(mod.__experimental_playground__) == bool


@pytest.mark.parametrize("extra", get_extras())
def test_extra_tests(extra: str):
    mod = import_module(f"streamlit_extras.{extra}")
    if hasattr(mod, "__tests__"):
        for test in mod.__tests__:
            test()
