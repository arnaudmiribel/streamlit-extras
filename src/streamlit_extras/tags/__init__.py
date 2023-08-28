import itertools
from typing import Literal

import streamlit as st

from .. import extra


def color(name):
    """Returns a color from the streamlit color palette, e.g. red-100, as hex."""
    try:
        hue, intensity = name.rsplit("-", 1)
    except (ValueError, KeyError):
        st.error(
            "Input color_name must contain a name (red, orange, ...) and"
            " intensity (10, 20, ... 100) e.g. 'red-70'"
        )
        st.stop()
    return ST_COLOR_PALETTE[hue][intensity]


ST_COLOR_PALETTE = {
    "red": {
        "100": "#7d353b",
        "90": "#bd4043",
        "80": "#ff2b2b",
        "70": "#ff4b4b",
        "60": "#ff6c6c",
        "50": "#ff8c8c",
        "40": "#ffabab",
        "30": "#ffc7c7",
        "20": "#ffdede",
        "10": "#fff0f0",
    },
    "orange": {
        "100": "#d95a00",
        "90": "#ed6f13",
        "80": "#ff8700",
        "70": "#ffa421",
        "60": "#ffbd45",
        "50": "#ffd16a",
        "40": "#ffe08e",
        "30": "#ffecb0",
        "20": "#fff6d0",
        "10": "#fffae8",
    },
    "yellow": {
        "100": "#dea816",
        "90": "#edbb16",
        "80": "#faca2b",
        "70": "#ffe312",
        "60": "#fff835",
        "50": "#ffff59",
        "40": "#ffff7d",
        "30": "#ffffa0",
        "20": "#ffffc2",
        "10": "#ffffe1",
    },
    "green": {
        "100": "#177233",
        "90": "#158237",
        "80": "#09ab3b",
        "70": "#21c354",
        "60": "#3dd56d",
        "50": "#5ce488",
        "40": "#7defa1",
        "30": "#9ef6bb",
        "20": "#c0fcd3",
        "10": "#dffde9",
    },
    "blue-green": {
        "100": "#246e69",
        "90": "#2c867c",
        "80": "#29b09d",
        "70": "#00d4b1",
        "60": "#20e7c5",
        "50": "#45f4d5",
        "40": "#6bfde3",
        "30": "#93ffee",
        "20": "#bafff7",
        "10": "#dcfffb",
    },
    "light-blue": {
        "100": "#15799e",
        "90": "#0d8cb5",
        "80": "#00a4d4",
        "70": "#00c0f2",
        "60": "#24d4ff",
        "50": "#4be4ff",
        "40": "#73efff",
        "30": "#9af8ff",
        "20": "#bffdff",
        "10": "#e0feff",
    },
    "blue": {
        "100": "#004280",
        "90": "#0054a3",
        "80": "#0068c9",
        "70": "#1c83e1",
        "60": "#3d9df3",
        "50": "#60b4ff",
        "40": "#83c9ff",
        "30": "#a6dcff",
        "20": "#c7ebff",
        "10": "#e4f5ff",
    },
    "violet": {
        "100": "#3f3163",
        "90": "#583f84",
        "80": "#6d3fc0",
        "70": "#803df5",
        "60": "#9a5dff",
        "50": "#b27eff",
        "40": "#c89dff",
        "30": "#dbbbff",
        "20": "#ebd6ff",
        "10": "#f5ebff",
    },
    "gray": {
        "100": "#0e1117",
        "90": "#262730",
        "80": "#555867",
        "70": "#808495",
        "60": "#a3a8b8",
        "50": "#bfc5d3",
        "40": "#d5dae5",
        "30": "#e6eaf1",
        "20": "#f0f2f6",
        "10": "#fafafa",
    },
}


HEADER_COLOR_CYCLE = itertools.cycle(
    [
        "light-blue-70",
        "orange-70",
        "blue-green-70",
        "blue-70",
        "violet-70",
        "red-70",
        "green-70",
        "yellow-80",
    ]
)

_SUPPORTED_COLORS = Literal[
    "light-blue-70",
    "orange-70",
    "blue-green-70",
    "blue-70",
    "violet-70",
    "red-70",
    "green-70",
    "yellow-80",
]

_DEFAULT_COLOR = "#808495"


@extra
def tagger_component(content: str, tags: list, color_name=None):
    """
    Displays tags next to your text.
    Args:
        content (str): Content to be tagged
        tags (list): A list of tags to be displayed next to the content
        color_name: choose from 'light-blue-70', orange-70, blue-green-70, 'blue-70', 'violet-70', 'red-70', 'green-70' and 'yellow-80'
    """
    if color_name and len(color_name) == len(tags):
        color_flag = True
    else:
        color_flag = False
    tags_html = content + " "
    for i in range(len(tags)):
        tags_html += "".join(
            [
                f"""
                                            <span style="display:inline-block;
                                            background-color: {color(color_name[i]) if color_flag else _DEFAULT_COLOR};
                                            padding: 0.1rem 0.5rem;
                                            font-size: 14px;
                                            font-weight: 400;
                                            color:white;
                                            margin: 5px;
                                            border-radius: 1rem;">{tags[i]}</span>"""
            ]
        )

    st.write(tags_html, unsafe_allow_html=True)


def example():
    tagger_component("Here is a feature request", ["p2", "🚩triaged", "backlog"])
    tagger_component(
        "Here are colored tags",
        ["turtle", "rabbit", "lion"],
        color_name=["light-blue-70", "orange-70", "blue-green-70"],
    )


__title__ = "Tags"
__desc__ = "Display tags like github issues!"
__icon__ = "🔖"
__examples__ = [example]
__author__ = "Maggie Liu"
__experimental_playground__ = False
