import streamlit as st
import validators


def add_logo(logo_url: str):
    """Add a logo (from logo_url) on the top of the navigation page of a multipage app.
    Taken from https://discuss.streamlit.io/t/put-logo-and-title-above-on-top-of-page-navigation-in-sidebar-of-multipage-app/28213/6

    Args:
        logo_url (HttpUrl): URL of the logo
    """

    validators.url(logo_url)

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({logo_url});
                background-repeat: no-repeat;
                padding-top: 80px;
                background-position: 20px 20px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def example():
    add_logo("http://placekitten.com/120/120")
    st.write("👈 Check out the cat in the nav-bar!")


__func__ = add_logo
__title__ = "App logo"
__desc__ = "Add a logo on top of the navigation bar of a multipage app"
__icon__ = "🐱"
__examples__ = [example]
__author__ = "Zachary Blackwood"
__experimental_playground__ = True
