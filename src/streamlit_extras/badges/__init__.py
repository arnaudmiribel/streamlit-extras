from __future__ import annotations

import html
from datetime import date
from typing import Literal, get_args

import streamlit as st

from .. import extra

_SUPPORTED_TYPES = Literal["pypi", "streamlit", "github", "twitter", "buymeacoffee"]


@extra
def badge(type: _SUPPORTED_TYPES, name: str | None = None, url: str | None = None) -> None:
    """Easily create a visual badge for PyPI, GitHub, Streamlit Cloud or other social platforms.

    Args:
        type (str): Badge type. Can be "pypi", "github", "streamlit", "twitter" or "buymeacoffee"
        name (str): Name of the PyPI package, GitHub repository, Twitter's username or BuyMeaCoffee Creator's page name.
                    Mandatory when using type="pypi", type="twitter" & type="buymeacoffee"
        url (str): URL of the Streamlit Cloud app. Mandatory when using type="streamlit"
    """

    assert type, "Type must be given!"

    assert type in get_args(_SUPPORTED_TYPES), (
        f"Input type '{type}' is not supported! Supported types are {get_args(_SUPPORTED_TYPES)}"
    )

    badge_html = None

    if type == "pypi":
        assert name, "You must give a valid PyPI package name!"
        name_escaped = html.escape(name, quote=True)
        badge_html = f'<a href="https://pypi.org/project/{name_escaped}"><img src="https://badge.fury.io/py/{name_escaped}.svg"></a>'

    if type == "streamlit":
        assert url, "You must provide a valid URL for the Streamlit app"
        url_escaped = html.escape(url, quote=True)
        badge_html = f'<a href="{url_escaped}"><img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg"></a>'

    if type == "github":
        assert name, "You must give a valid GitHub repository name! Something like 'author/name'"
        name_escaped = html.escape(name, quote=True)
        badge_html = f'<a href="https://github.com/{name_escaped}"><img src="https://img.shields.io/github/stars/{name_escaped}.svg?style=social&label=Star&maxAge=2592000"></a>'

    if type == "twitter":
        assert name, "You must provide a valid twitter username"
        name_escaped = html.escape(name, quote=True)
        badge_html = f'<a href="https://twitter.com/intent/follow?screen_name={name_escaped}"><img src="https://img.shields.io/twitter/follow/{name_escaped}?style=social&logo=twitter"></a>'

    if type == "buymeacoffee":
        assert name, "You must provide a valid Buy-Me-a-Coffee page username"
        name_escaped = html.escape(name, quote=True)
        badge_html = f'<a href="https://www.buymeacoffee.com/{name_escaped}"><img src="https://img.shields.io/badge/Buy%20me%20a%20coffee--yellow.svg?logo=buy-me-a-coffee&logoColor=orange&style=social"></a>'

    if badge_html is not None:
        st.html(badge_html)


def example_pypi() -> None:
    badge(type="pypi", name="plost")
    badge(type="pypi", name="streamlit")


def example_streamlit() -> None:
    badge(type="streamlit", url="https://plost.streamlitapp.com")


def example_github() -> None:
    badge(type="github", name="streamlit/streamlit")


def example_twitter() -> None:
    badge(type="twitter", name="streamlit")


def example_buymeacoffee() -> None:
    badge(type="buymeacoffee", name="andfanilo")


__title__ = "Badges"
__desc__ = "Create custom badges (e.g. PyPI, Streamlit Cloud, GitHub, Twitter, Buy Me a Coffee)"
__icon__ = "🏷️"
__examples__ = [
    example_pypi,
    example_streamlit,
    example_github,
    example_twitter,
    example_buymeacoffee,
]
__author__ = "Arnaud Miribel, ShruAgarwal"
__created_at__ = date(2022, 8, 18)
__playground__ = True
