import streamlit as st
from streamlit_book import set_chapter_config as st_book

from .. import extra

st_book = extra(st_book)


def example():
    st.write("## Streamlit Book")
    st_book(path="st_book/pages/chapter")


__title__ = "Streamlit Book - Multipaging Demo"
__desc__ = "A companion library to create a interactive reader for the content on a given folder"
__icon__ = "📙"
__examples__ = [example]
__author__ = "Sebastian Flores"
__pypi_name__ = "streamlit-book"
__package_name__ = "streamlit_book"
__github_repo__ = "sebastiandres/streamlit_book"
__forum_url__ = "https://discuss.streamlit.io/t/happy-birds-showcasing-the-streamlit-book-library/20012"  # Optional
__experimental_playground__ = False  # Optional
