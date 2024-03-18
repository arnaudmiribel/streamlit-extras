import base64
from pathlib import Path

import streamlit as st
import validators

from .. import extra


@extra
def add_logo(logo_url: str, title: str = "", subtitle: str = "", height: int = 200, color: str = "black", switch_position: bool = False):
    """Add a logo (and optionally a title and subtitle) on the top of the navigation page of a multipage app.
    Is it possible to choose also the color and the position of both element, if above or below the Logo.
    The url can either be a URL to the image or a local path to the image.

    Args:
        logo_url (str): URL/local path of the logo
        title (str, optional): Title to be displayed above or below the logo, depending on switch_position.
        subtitle (str, optional): Subtitle to be displayed below the name or above the logo, depending on switch_position.
        height (int, optional): Height of the logo. Defaults to 200.
        color (str, optional): Color of title and subtitle. Default to black.
        switch_position (bool, optional): Switches the position of the logo and title if True. Defaults to False, so
                                          first Title and later Logo, as order.
    """

    if validators.url(logo_url):
        logo = f"url({logo_url})"
    else:
        # Convert the local image to a base64 string
        logo = f"url(data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()})"

    # Adjust padding-top based on whether title and subtitle are provided
    padding_top = height + 70 if title or subtitle else height + 70

    # Determine the position of the title and logo based on switch_position
    title_top = "20px" if not switch_position else f"{height + 50}px"
    logo_top = f"{height-70}px" if not switch_position else "20px"

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: none;
                padding-top: {padding_top}px;
            }}
            
            [data-testid="stSidebarNav"]::before {{
                content: "{title}\\A{subtitle}";
                display: block;
                position: absolute;
                top: {title_top};
                left: 0;
                right: 0;
                white-space: pre-wrap;
                text-align: center;
                color: {color};
                font-size: 18px;
                font-weight: bold;
            }}
            
            [data-testid="stSidebarNav"]::after {{
                content: "";
                display: block;
                position: absolute;
                top: {logo_top};
                left: 20px;
                right: 20px;
                height: {height}px;
                background-image: {logo};
                background-repeat: no-repeat;
                background-size: contain;
                background-position: center;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def example():
    if st.checkbox("Use url", value=True):
        add_logo("http://placekitten.com/120/120")
    else:
        add_logo("gallery/kitty.jpeg", height=300)
    st.write("👈 Check out the cat in the nav-bar!")


__title__ = "App logo"
__desc__ = "Add a logo on top of the navigation bar of a multipage app"
__icon__ = "🐱"
__examples__ = [example]
__author__ = "Zachary Blackwood"
__experimental_playground__ = True
