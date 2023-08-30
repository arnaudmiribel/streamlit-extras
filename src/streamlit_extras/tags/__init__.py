from __future__ import annotations

import streamlit as st

from .. import extra

# mypy: ignore-errors
TAGGER_COLOR_PALETTE = {
    "lightblue": "#00c0f2",
    "orange": "#ffa421",
    "bluegreen": "#00d4b1",
    "blue": "#1c83e1",
    "violet": "#803df5",
    "red": "#ff4b4b",
    "green": "#21c354",
    "yellow": "#faca2b",
}


@extra
def tagger_component(
    content: str, tags: list, color_name: list[str] | str | None = None
):
    """
    Displays tags next to your text.
    Args:
        content (str): Content to be tagged
        tags (list): A list of tags to be displayed next to the content
        color_name: A list or a string that indicates the color of tags.
        Choose from lightblue, orange, bluegreen, blue, violet, red, green, yellow
    """
    if color_name is None:
        _DEFAULT_COLOR = "#808495"
        color_flag = False
    else:
        for color in color_name:
            if color not in [
                "lightblue",
                "orange",
                "bluegreen",
                "blue",
                "violet",
                "red",
                "green",
                "yellow",
            ]:
                st.error(
                    "color_name must contain a name from lightblue, orange, bluegreen, blue, violet, red, green, yellow"
                )
                st.stop()
        if color_name and len(color_name) == len(tags):
            color_flag = True
        elif len(color_name) == 1:
            _DEFAULT_COLOR = TAGGER_COLOR_PALETTE[color_name]  # type: ignore
            color_flag = False

    tags_html = content + " "
    for i in range(len(tags)):
        tags_html += "".join(
            [
                f"""
                <span style="display:inline-block;
                background-color: {TAGGER_COLOR_PALETTE[color_name[i]] if color_flag else _DEFAULT_COLOR}
                padding: 0.1rem 0.5rem;
                font-size: 14px;
                font-weight: 400;
                color:white;
                margin: 5px;
                border-radius: 1rem;">{tags[i]}</span>"""
            ]  # type: ignore
        )

    st.write(tags_html, unsafe_allow_html=True)


def example():
    tagger_component("Here is a feature request", ["p2", "🚩triaged", "backlog"])
    tagger_component(
        "Here are colored tags",
        ["turtle", "rabbit", "lion"],
        color_name=["blue", "orange", "lightblue"],
    )
    tagger_component(
        "Annotate the feature",
        ["hallucination"],
        color_name=["blue"],
    )


__title__ = "Tags"
__desc__ = "Display tags like github issues!"
__icon__ = "🔖"
__examples__ = [example]
__author__ = "Maggie Liu"
__experimental_playground__ = False
