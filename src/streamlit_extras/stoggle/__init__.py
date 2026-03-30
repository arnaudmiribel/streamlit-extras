import html
from datetime import date

import streamlit as st

from .. import extra


@extra
def stoggle(summary: str, content: str) -> None:
    """
    Displays a toggle widget in Streamlit

    Args:
        summary (str): Summary of the toggle (always shown)
        content (str): Content shown after toggling
    """

    summary_escaped = html.escape(summary)
    content_escaped = html.escape(content)
    html_str = f'<div style="line-height:1.8"><details><summary>{summary_escaped}</summary><p>{content_escaped}</p></details></div>'
    st.html(html_str)


def example() -> None:
    stoggle(
        "Click me!",
        """🥷 Surprise! Here's some additional content""",
    )


__title__ = "Toggle button"
__desc__ = "Toggle button just like in Notion!"
__icon__ = "➡️"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__created_at__ = date(2022, 8, 10)
__github_repo__ = "arnaudmiribel/stoggle"
__streamlit_cloud_url__ = "http://stoggle.streamlitapp.com"
__playground__ = True
