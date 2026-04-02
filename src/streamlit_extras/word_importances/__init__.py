from collections.abc import Sequence
from datetime import date

import streamlit as st

from .. import extra


def get_mode() -> str:
    if hasattr(st.context, "theme"):
        return st.context.theme["type"]
    return "light"


@extra
def format_word_importances(words: Sequence[str], importances: Sequence[float]) -> str:
    """Adds a background color to each word based on its importance (float from -1 to 1)

    Args:
        words (list): List of words
        importances (list): List of importances (scores from -1 to 1)

    Returns:
        html (str): HTML string with formatted word


    """
    if importances is None or len(importances) == 0:
        return "<td></td>"
    assert len(words) == len(importances), "Words and importances but be of same length"

    tags = ["<td>"]
    for word, importance in zip(words, importances[: len(words)], strict=False):
        mode = get_mode()
        color = _get_color(importance, mode)
        font_color = "black" if mode == "light" else "white"
        unwrapped_tag = (
            f'<mark style="background-color: {color}; opacity:1.0;             '
            f'        line-height:1.75"><font color="{font_color}"> {word}            '
            "        </font></mark>"
        )
        tags.append(unwrapped_tag)
    tags.append("</td>")
    return "".join(tags)


def _get_color(importance: float, mode: str | None = None) -> str:
    mode = mode or get_mode()
    # clip values to prevent CSS errors (Values should be from [-1,1])
    importance = max(-1, min(1, importance))
    if importance > 0:
        hue = 120
        sat = 75
        lig_mod = int(50 * importance)
    else:
        hue = 0
        sat = 75
        lig_mod = int(-40 * importance)
    lig = 0 + lig_mod if mode == "dark" else 100 - lig_mod

    return f"hsl({hue}, {sat}%, {lig}%)"


def example() -> None:
    text = "Streamlit Extras is a library to help you discover, learn, share and use Streamlit bits of code!"
    html = format_word_importances(
        words=text.split(),
        importances=[
            0.1,
            0.2,
            0,
            -1,
            0.1,
            0,
            0,
            0.2,
            0.3,
            0.8,
            0.9,
            0.6,
            0.3,
            0.1,
            0,
            0,
            0,
        ],
    )
    st.html(html)


__title__ = "Word importances"
__desc__ = "Highlight words based on their importances. Inspired from captum library."
__icon__ = "❗"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__created_at__ = date(2022, 9, 20)
__playground__ = True
