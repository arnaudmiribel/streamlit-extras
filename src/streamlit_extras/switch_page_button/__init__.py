import streamlit as st

from .. import extra


@extra
def switch_page(page_name: str):
    """
    Switch page programmatically in a multipage app

    Args:
        page_name (str): Target page name
    """

    try:
        from streamlit.runtime.scriptrunner import RerunData, RerunException
    except ModuleNotFoundError:  # For streamlit > 1.37
        from streamlit.runtime.scriptrunner_utils.exceptions import RerunException
        from streamlit.runtime.scriptrunner_utils.script_requests import RerunData

    try:
        from streamlit.source_util import get_pages
    except ImportError as err:
        raise ImportError(
            "switch_page is no longer supported with this version of Streamlit. "
            "Please use st.switch_page() instead: "
            "https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page"
        ) from err

    def standardize_name(name: str) -> str:
        return name.lower().replace("_", " ")

    page_name = standardize_name(page_name)

    pages = get_pages("streamlit_app.py")  # OR whatever your main page is called

    for page_hash, config in pages.items():
        if standardize_name(config["page_name"]) == page_name:
            raise RerunException(
                RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )

    page_names = [standardize_name(config["page_name"]) for config in pages.values()]

    raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")


def example():
    want_to_contribute = st.button("I want to contribute!")
    if want_to_contribute:
        switch_page("Contribute")


def test_switch_page():
    import pytest

    try:
        from streamlit.source_util import get_pages  # noqa: F401
    except ImportError:
        pytest.skip(
            "streamlit.source_util.get_pages removed; use st.switch_page() instead"
        )

    try:
        from streamlit.runtime.scriptrunner import RerunException
    except ModuleNotFoundError:
        from streamlit.runtime.scriptrunner_utils.exceptions import RerunException

    with pytest.raises(RerunException):
        switch_page("streamlit app")


def test_switch_invalid_page():
    import pytest

    try:
        from streamlit.source_util import get_pages  # noqa: F401
    except ImportError:
        pytest.skip(
            "streamlit.source_util.get_pages removed; use st.switch_page() instead"
        )

    with pytest.raises(ValueError):
        switch_page("non existent page")


__title__ = "Switch page function"
__desc__ = """Function to switch page programmatically in a MPA.
**Note:** [st.switch_page](https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page) has been released in Streamlit 1.37.0!"""
__icon__ = "🖱️"
__examples__ = [example]
__author__ = "Zachary Blackwood"
__tests__ = [test_switch_page, test_switch_invalid_page]
__deprecated__ = True
