"""Resizable columns for Streamlit.

A drop-in replacement for st.columns that lets users drag dividers to resize columns interactively.
Column widths persist across reruns via component state.
"""

from collections.abc import Sequence
from datetime import date
from functools import cache
from typing import Any

import streamlit as st
import streamlit.components.v2
import streamlit.errors
from streamlit.delta_generator import DeltaGenerator

from streamlit_extras import extra


def _on_widths_change() -> None:
    pass


@cache
def _get_component() -> Any:
    return streamlit.components.v2.component(
        "streamlit-extras.resizable_columns",
        js="index-*.js",
        html='<div class="react-root"></div>',
        isolate_styles=False,
    )


@extra
def resizable_columns(
    num_columns: int | Sequence[int | float] = 2,
    *,
    min_width: int = 50,
    border: bool = False,
    key: str | None = None,
) -> list[DeltaGenerator]:
    """Display resizable columns that users can drag to adjust widths.

    Works like st.columns but with draggable dividers between columns. Column widths
    are persisted across reruns.

    Args:
        num_columns: Number of columns (int) or list of initial width ratios (e.g. [1, 2, 1]).
        min_width: Minimum column width in pixels. Prevents collapsing columns to zero.
        border: If True, show a border around each column.
        key: Unique key for this widget instance.

    Returns:
        A list of column containers (DeltaGenerator) to place content in.

    Example:

        ```python
        cols = resizable_columns(3)
        cols[0].write("Left")
        cols[1].write("Center")
        cols[2].write("Right")
        ```

    Raises:
        StreamlitAPIException: If less than 1 column is specified.
    """
    if isinstance(num_columns, int):
        n = num_columns
        initial_widths = [1.0 / n] * n
    else:
        ratios = list(num_columns)
        n = len(ratios)
        total = sum(ratios)
        initial_widths = [r / total for r in ratios]

    if n < 1:
        raise st.errors.StreamlitAPIException("Must have at least 1 column.")

    effective_key = key or "resizable_columns_default"
    component_state = st.session_state.get(effective_key, {})
    stored_widths = component_state.get("widths")

    widths = [float(w) for w in stored_widths] if stored_widths and len(stored_widths) == n else initial_widths

    component = _get_component()
    component(
        key=effective_key,
        data={
            "num_columns": n,
            "widths": widths,
            "min_width": min_width,
        },
        default={"widths": initial_widths},
        on_widths_change=_on_widths_change,
        height=1,
    )

    result_state = st.session_state.get(effective_key, {})
    final_widths = result_state.get("widths", widths)
    col_spec = [max(w, 0.01) for w in final_widths] if final_widths and len(final_widths) == n else widths

    return list(st.columns(col_spec, border=border))


def example_basic() -> None:
    """Basic resizable columns."""
    st.write("### Drag the handles between columns to resize")
    cols = resizable_columns(3, key="basic_demo")
    with cols[0]:
        st.header("Left")
        st.write("This is the left column. Drag the divider to resize.")
    with cols[1]:
        st.header("Center")
        st.write("This is the center column.")
    with cols[2]:
        st.header("Right")
        st.write("This is the right column.")


def example_with_ratios() -> None:
    """Columns with initial width ratios."""
    st.write("### Custom initial ratios [1, 3, 1]")
    cols = resizable_columns([1, 3, 1], key="ratio_demo")
    with cols[0]:
        st.metric("Sidebar", "42")
    with cols[1]:
        st.line_chart({"data": [1, 5, 2, 6, 2, 1]})
    with cols[2]:
        st.metric("Info", "99%")


def example_with_border() -> None:
    """Resizable columns with borders."""
    st.write("### Bordered resizable columns")
    cols = resizable_columns(3, border=True, key="border_demo")
    with cols[0]:
        st.metric("Revenue", "$12.4k", "+8%")
    with cols[1]:
        st.metric("Users", "1,024", "+12%")
    with cols[2]:
        st.metric("Uptime", "99.9%", "+0.1%")


def example_two_panel() -> None:
    """Two-panel resizable layout."""
    st.write("### Two-panel layout")
    left, right = resizable_columns([1, 2], key="two_panel_demo")
    with left:
        option = st.radio("Select view", ["Chart", "Table", "Summary"])
        st.write(f"Selected: {option}")
    with right:
        st.write("Main content area")
        st.bar_chart({"values": [3, 6, 2, 8, 4]})


__title__ = "Resizable Columns"
__desc__ = "Drag-to-resize columns, a drop-in replacement for st.columns with interactive dividers."
__icon__ = "↔️"
__author__ = "streamlit-extras"
__created_at__ = date(2026, 3, 26)
__examples__ = [example_with_border, example_basic, example_with_ratios, example_two_panel]
