from typing import Sequence

import re
import streamlit as st
from streamlit_extras import grid

from .. import extra

@extra
def button_selector(key: str, candidate_list: Sequence[str], col_number: int = 4, default: int = 0) -> int:
    """
    Create a button selector for choosing an item from a list of candidates.

    This function creates a grid of buttons representing the items in the provided list.
    The selected button is highlighted, and the index of the selected item is returned.

    Args:
        key (str): A unique key for the button selector. Used for maintaining state.
        candidate_list (Sequence[str]): A list of strings representing the selectable options.
        col_number (int, optional): The number of columns in the button grid. Defaults to 4.
        default (int, optional): The index of the default selected item. Defaults to 0.

    Returns:
        int: The index of the currently selected item in the candidate_list.

    Note:
        This function uses Streamlit's session state to maintain the selected item
        across reruns of the app.
    """

    def incre_str(s: str) -> str:
        return re.sub(r'(?:(\d+))?$', lambda x: '_0' if x.group(1) is None else str(int(x.group(1)) + 1), s)

    def get_selected_index() -> int:
        if key not in st.session_state:
            st.session_state[key] = default
        index = st.session_state.get(key)
        if index not in range(len(candidate_list)):
            index = default
        return index

    def set_selected(index: int, button_key: str):
        st.session_state[key] = index
        # refreshe botton status
        st.session_state[button_key] = incre_str(st.session_state[button_key])

    num = len(candidate_list)
    grid_numbers = [col_number] * (num // col_number + 1)
    g: st = grid(*grid_numbers)

    for index, name in enumerate(candidate_list):
        t = "primary" if index == get_selected_index() else "secondary"
        button_key = f"{key}_{name}"
        st.session_state[button_key] = f"{button_key}_value_0"
        g.button(name, key=st.session_state[button_key], use_container_width=True, type=t, on_click=set_selected, args=(index, button_key))

    return get_selected_index()

def example():
    month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_index = button_selector("button_selector_example_month_selector", month_list, 4, 0)
    st.write(f"Selected month: {month_list[selected_index]}")


__title__ = "Button Selector"
__desc__ = "A button selector that can be used to select a candidate from a list of candidates."
__icon__ = "🔢"
__examples__ = [example]
__author__ = "Zhijia Liu"
__experimental_playground__ = False
