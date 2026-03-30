from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from .. import extra


def toggle_state(key: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = False

    st.session_state[key] = not st.session_state[key]


@extra
def button(*args: Any, key: str | None = None, **kwargs: Any) -> bool:
    """Create a toggle button that remembers its state.

    Works just like a normal streamlit button, but it remembers its state, so that
    it works as a toggle button. If you click it, it will be pressed, and if you click
    it again, it will be unpressed. Args and output are the same as for st.button.

    Args:
        *args: Positional arguments passed to st.button.
        key (str | None): Required unique key for the button. Must not be None.
        **kwargs: Keyword arguments passed to st.button.

    Returns:
        bool: True if the button is currently in pressed state, False otherwise.

    Raises:
        ValueError: If key is not provided.
    """

    if key is None:
        raise ValueError("Must pass key")

    if key not in st.session_state:
        st.session_state[key] = False

    if "type" not in kwargs:
        kwargs["type"] = "primary" if st.session_state[key] else "secondary"

    derived_key = f"{key}_derived"

    original_on_click = kwargs.get("on_click")

    def callback() -> None:
        if original_on_click is not None:
            original_on_click()
        toggle_state(key)

    kwargs["on_click"] = callback

    st.button(*args, key=derived_key, **kwargs)  # type: ignore[misc]

    return st.session_state[key]


def example() -> None:
    if button("Button 1", key="button1") and button("Button 2", key="button2"):
        if button("Button 3", key="button3"):
            st.write("All 3 buttons are pressed")


__title__ = "Stateful Button"
__desc__ = "Button that keeps track of its state, so that it works as a toggle button"
__icon__ = "🔛"
__examples__ = [example]
__author__ = "Zachary Blackwood"
__created_at__ = date(2022, 12, 21)
__forum_url__ = "https://discuss.streamlit.io/t/how-to-use-multiple-buttons-in-st-columns/35088/4?u=blackary"
__playground__ = True
