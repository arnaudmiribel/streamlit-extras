import re
from typing import Optional, Sequence

import streamlit as st

from streamlit_extras.grid import grid

from .. import extra


@extra
def button_selector(
    options: Sequence[str],
    index: int = 0,
    spec: int = 4,
    key: str = "button_selector",
    label: Optional[str] = None,
) -> int:
    """
    Create a button selector for choosing an item from a list of options.

    This function creates a grid of buttons representing the items in the provided list.
    The selected button is highlighted, and the index of the selected item is returned.

    Args:
        options (Sequence[str]): A list of strings representing the selectable options.
        index (int, optional): The index of the default selected item. Defaults to 0.
        spec (int, optional): The number of columns in the button grid. Defaults to 4.
        key (str, optional): A unique key for the button selector. Used for maintaining state.
        label (str, optional): A label for the button selector. Defaults to None.

    Returns:
        int: The index of the currently selected item in the options.

    Note:
        This function uses Streamlit's session state to maintain the selected item
        across reruns of the app.
    """

    def incre_str(s: str) -> str:
        return re.sub(
            r"(?:(\d+))?$",
            lambda x: "_0" if x.group(1) is None else str(int(x.group(1)) + 1),
            s,
        )

    def get_selected_index() -> int:
        if key not in st.session_state:
            st.session_state[key] = index
        selected_index = st.session_state.get(key)
        if selected_index not in range(len(options)):
            selected_index = index
        return selected_index

    def set_selected(selected_index: int, button_key: str):
        st.session_state[key] = selected_index
        # refresh the button's state
        st.session_state[button_key] = incre_str(st.session_state[button_key])

    if label is not None:
        st.caption(f":gray[{label}]")

    num = len(options)
    grid_numbers = [spec] * (num // spec + 1)
    g = grid(*grid_numbers)

    for id, name in enumerate(options):
        t = "primary" if id == get_selected_index() else "secondary"
        button_key = f"{key}_{name}"
        st.session_state[button_key] = f"{button_key}_value_0"
        g.button(
            name,
            key=st.session_state[button_key],
            use_container_width=True,
            type=t,
            on_click=set_selected,
            args=(id, button_key),
        )

    return get_selected_index()


def example():
    month_list = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    selected_index = button_selector(
        month_list,
        index=0,
        spec=4,
        key="button_selector_example_month_selector",
        label="Month Selector",
    )
    st.write(f"Selected month: {month_list[selected_index]}")


__title__ = "Button Selector"
__desc__ = (
    "A button selector that can be used to select an item from a list of options."
)
__icon__ = "🔢"
__examples__ = [example]
__author__ = "Zhijia Liu"
__experimental_playground__ = False
