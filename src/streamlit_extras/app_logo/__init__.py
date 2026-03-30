import base64
from datetime import date
from pathlib import Path

import streamlit as st
from streamlit.deprecation_util import show_deprecation_warning

from .. import extra
from ..utils import is_url


@extra
def add_logo(logo_url: str, height: int = 120) -> None:
    """Add a logo (from logo_url) on the top of the navigation page of a multipage app.

    Taken from the Streamlit forum. The url can either be a url to the image, or a local
    path to the image.

    Args:
        logo_url (str): URL/local path of the logo

    !!! warning "Deprecated"
        This function is deprecated. Use
        [`st.logo()`](https://docs.streamlit.io/develop/api-reference/media/st.logo)
        instead.
    """
    show_deprecation_warning(
        "add_logo is deprecated. Use `st.logo()` instead. "
        "See https://docs.streamlit.io/develop/api-reference/media/st.logo",
        show_once=True,
    )

    if is_url(logo_url):
        logo = f"url({logo_url})"
    else:
        logo = f"url(data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()})"

    st.html(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: {logo};
                background-repeat: no-repeat;
                padding-top: {height - 40}px;
                background-position: 20px 20px;
            }}
        </style>
        """
    )


def example() -> None:
    if st.checkbox("Use url", value=True):
        add_logo("http://placekitten.com/120/120")
    else:
        add_logo("gallery/kitty.jpeg", height=300)
    st.write("👈 Check out the cat in the nav-bar!")


__title__ = "App logo"
__desc__ = """Add a logo on top of the navigation bar of a multipage app.
**Note:** [st.logo](https://docs.streamlit.io/develop/api-reference/media/st.logo) has been released in Streamlit 1.35.0!"""
__icon__ = "🐱"
__examples__ = [example]
__author__ = "Zachary Blackwood"
__created_at__ = date(2022, 8, 18)
__playground__ = False
__deprecated__ = True
