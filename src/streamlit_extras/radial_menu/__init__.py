"""Radial menu component for Streamlit.

A circular menu that displays options in a ring around a central button.
This is an example of a Type D CCv2 extra (with dedicated asset files).
"""

from datetime import date
from pathlib import Path
from typing import TypedDict

from streamlit_extras import extra
from streamlit_extras._component_utils import register_file_component

_COMPONENT = register_file_component(
    "streamlit_extras.radial_menu",
    Path(__file__).parent,
)


class RadialMenuState(TypedDict):
    """State returned by the radial menu component."""

    selection: str | None


@extra
def radial_menu(
    options: dict[str, str],
    *,
    default: str | None = None,
    key: str = "radial_menu",
) -> RadialMenuState:
    """Display a radial menu with the given options.

    Args:
        options: A dictionary mapping option values to their display icons/emojis.
            Example: {"home": "🏠", "search": "🔍", "settings": "⚙️"}
        default: The default selected option. If None, uses the first option.
        key: A unique key for this component instance.

    Returns:
        A TypedDict with a "selection" key containing the currently selected option value.

    Example:

        ```python
        result = radial_menu({"home": "🏠", "search": "🔍", "settings": "⚙️"})
        st.write(f"Selected: {result['selection']}")
        ```
    """
    if default is None:
        default = next(iter(options.keys()), None)

    return _COMPONENT(
        key=key,
        data={"options": options, "selection": default},
        default={"selection": default},
        on_selection_change=lambda: None,
    )


def example() -> None:
    """Example usage of the radial menu component."""
    import streamlit as st

    st.write("Click the button below to open the radial menu:")

    result = radial_menu(
        options={
            "home": "🏠",
            "search": "🔍",
            "settings": "⚙️",
            "profile": "👤",
            "help": "❓",
        },
        key="demo_menu",
    )

    st.write(f"**Selected:** `{result['selection']}`")


__title__ = "Radial Menu"
__desc__ = "A circular menu component that displays options in a ring around a central button."
__icon__ = "🎯"
__examples__ = [example]
__author__ = "Debbie Matthews"
__created_at__ = date(2026, 3, 24)
