import streamlit as st
from htbuilder import details, div, p, styles
from htbuilder import summary as smry


def stoggle(summary: str, content: str):
    """
    Displays a toggle widget in Streamlit
    Args:
        summary (str): Summary of the toggle (always shown)
        content (str): Content shown after toggling
    """

    st.write(
        str(
            div(
                style=styles(
                    line_height=1.8,
                )
            )(details(smry(summary), p(content)))
        ),
        unsafe_allow_html=True,
    )


def example():
    stoggle(
        "Click me!",
        """🥷 Surprise! Here's some additional content""",
    )
