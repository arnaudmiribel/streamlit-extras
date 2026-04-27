import pkgutil
from importlib import import_module
from pathlib import Path

import pytest
import toml

import streamlit_extras

EXTRAS_DIR = Path(__file__).parent.parent / "src" / "streamlit_extras"
CCv2_MANIFEST = EXTRAS_DIR / "pyproject.toml"


def get_extras() -> list[str]:
    return [extra.name for extra in pkgutil.iter_modules(streamlit_extras.__path__) if extra.ispkg]


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


def test_ccv2_manifest_contains_all_react_extras() -> None:
    """Verify the CCv2 pyproject.toml manifest is in sync with React-based extras.

    Every extra that ships a frontend/package.json must be declared in
    src/streamlit_extras/pyproject.toml with an asset_dir entry.  If this
    test fails it means a new React extra was added (or removed) without
    updating the manifest - which would cause a StreamlitAPIException at
    runtime for any user of that component.
    """
    # Extras that have a frontend/package.json (i.e. React-based CCv2 extras)
    react_extras = sorted(
        p.parent.parent.name
        for p in EXTRAS_DIR.glob("*/frontend/package.json")
    )

    assert CCv2_MANIFEST.exists(), (
        f"CCv2 manifest not found at {CCv2_MANIFEST}. "
        "Run `uv build` to regenerate it."
    )

    manifest_data = toml.loads(CCv2_MANIFEST.read_text())
    declared_components: list[dict[str, str]] = (
        manifest_data.get("tool", {})
        .get("streamlit", {})
        .get("component", {})
        .get("components", [])
    )
    declared_names = {c["name"] for c in declared_components if "name" in c}

    missing = sorted(set(react_extras) - declared_names)
    assert not missing, (
        f"The following React extras have a frontend/package.json but are NOT "
        f"declared in {CCv2_MANIFEST.relative_to(EXTRAS_DIR.parent.parent)}:\n"
        + "\n".join(f"  - {name}" for name in missing)
        + "\nUpdate the manifest by running `uv build` and committing the result."
    )

    extra_entries = sorted(declared_names - set(react_extras))
    assert not extra_entries, (
        "The following names are declared in the CCv2 manifest but have no "
        "corresponding frontend/package.json:\n"
        + "\n".join(f"  - {name}" for name in extra_entries)
        + "\nRemove stale entries from the manifest."
    )
