import streamlit as st

from .. import extra


@extra
def tagger_component(content: str, tags: list):
    """
    Displays tags next to your text.
    Args:
        content (str): Content to be tagged
        tags (list): A list of tags to be displayed next to the content
    """

    tags_html = (
        content
        + " "
        + "".join(
            [
                f"""
                                        <span style="display:inline-block;
                                        background-color: #e0e0e0;
                                        padding: 0.1rem 0.5rem;
                                        font-size: 14px;
                                        font-weight: 400;
                                        margin: 5px;
                                        border-radius: 1rem;">{tag}</span>"""
                for tag in tags
            ]
        )
    )

    st.write(tags_html, unsafe_allow_html=True)


def example():
    tagger_component("Here is a feature request", ["p2", "🚩triaged", "backlog"])


__title__ = "Tags"
__desc__ = "Display tags like github issues!"
__icon__ = "🔖"
__examples__ = [example]
__author__ = "Maggie Liu"
__experimental_playground__ = True
