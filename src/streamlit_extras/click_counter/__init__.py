"""Click counter component for Streamlit.

A simple interactive counter built with React and CCv2.
This is an example of a Type E CCv2 extra (React + Vite bundling).
"""

from functools import cache
from typing import Any, TypedDict, cast

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra


def _on_count_change() -> None:
    """Callback function for when the count changes in the frontend."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.click_counter",
        js="index-*.js",
        html='<div class="react-root"></div>',
    )


class ClickCounterState(TypedDict):
    """State returned by the click counter component."""

    count: int


@extra
def click_counter(
    *,
    label: str = "Click Me!",
    initial_count: int = 0,
    key: str | None = None,
) -> ClickCounterState:
    """Display an interactive click counter.

    A simple React-based component that demonstrates the CCv2 pattern
    for building interactive Streamlit components with React.

    Args:
        label: The text to display on the button.
        initial_count: The initial count value.
        key: A unique key for this component instance.

    Returns:
        A TypedDict with a "count" key containing the current count.

    Example:
        >>> result = click_counter(label="Click to increment!", key="my_counter")
        >>> st.write(f"Count: {result['count']}")
    """
    component = _get_component()
    return cast(
        "ClickCounterState",
        component(
            key=key,
            data={"label": label},
            default={"count": initial_count},
            on_count_change=_on_count_change,
        ),
    )


def example() -> None:
    """Example usage of the click counter component."""
    st.write("Click the button below to increment the counter:")

    result = click_counter(
        label="Click Me! 🎉",
        initial_count=0,
        key="demo_counter",
    )

    st.write(f"**Current count:** `{result['count']}`")


__title__ = "Click Counter"
__desc__ = "An interactive click counter component built with React and CCv2."
__icon__ = "🔢"
__examples__ = [example]
__author__ = "streamlit-extras"
__streamlit_min_version__ = "1.46.0"
