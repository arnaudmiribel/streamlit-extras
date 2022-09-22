from importlib import import_module
from pathlib import Path
from typing import List

import pytest

PATH_TO_EXTRAS = "src/streamlit_extras"


def get_extras() -> List[str]:
    extra_names = [
        folder.name
        for folder in Path(PATH_TO_EXTRAS).glob("*")
        if folder.is_dir() and folder.name != "__pycache__"
    ]
    return extra_names


@pytest.mark.parametrize("extra", get_extras())
def test_extra_attributes(extra: str):
    mod = import_module(f"{PATH_TO_EXTRAS.replace('/', '.')}.{extra}")
    assert type(mod.__title__) == str
    assert type(mod.__icon__) == str
    assert type(mod.__desc__) == str
    assert callable(mod.__func__)
    assert len(mod.__examples__) > 0
    assert type(mod.__author__) == str
    if hasattr(mod, "__inputs__"):
        assert type(mod.__inputs__) == dict
    if hasattr(mod, "__github_repo__"):
        assert type(mod.__github_repo__) == str
    if hasattr(mod, "__pypi_name__"):
        assert type(mod.__pypi_name__) == str
    if hasattr(mod, "__package_name__"):
        assert type(mod.__package_name__) == str
    if hasattr(mod, "__streamlit_cloud_url__"):
        assert type(mod.__streamlit_cloud_url__) == str
    if hasattr(mod, "__twitter_username__"):
        assert type(mod.__twitter_username__) == str
    if hasattr(mod, "__buymeacoffee_username__"):
        assert type(mod.__buymeacoffee_username__) == str
    if hasattr(mod, "__experimental_playground__"):
        assert type(mod.__experimental_playground__) == bool
