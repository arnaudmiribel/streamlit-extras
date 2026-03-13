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

    html = f'<div style="line-height:1.8"><details><summary>{summary}</summary><p>{content}</p></details></div>'
    st.html(html)


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
__github_repo__ = "arnaudmiribel/stoggle"
__streamlit_cloud_url__ = "http://stoggle.streamlitapp.com"
__playground__ = True
