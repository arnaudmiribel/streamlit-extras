"""Pagination widget for Streamlit.

A pagination widget for navigating through pages of content with numbered page buttons,
prev/next arrows, and intelligent truncation for large page counts.
"""

from collections.abc import Callable
from datetime import date
from functools import cache
from typing import Any, Literal

import streamlit as st
import streamlit.components.v2
import streamlit.errors

from streamlit_extras import extra


def _on_page_change() -> None:
    """Callback function for when the page changes in the frontend."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.pagination",
        js="index-*.js",
        html='<div class="react-root"></div>',
    )


@extra
def pagination(
    num_pages: int,
    *,
    default: int = 1,
    key: str | None = None,
    on_change: Callable[..., None] | None = None,
    args: tuple[Any, ...] | list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    max_visible_pages: int | None = 7,
    width: Literal["content", "stretch"] | int = "content",
) -> int:
    """Display a pagination widget for navigating through pages.

    The widget displays numbered page buttons with prev/next arrows and intelligent
    truncation for large page counts. One page is always selected (stateful), and
    the widget returns the currently selected page number.

    Args:
        num_pages: Total number of pages. Must be >= 1.
        default: Initial selected page (1-indexed). Must be between 1 and num_pages.
        key: Unique key for the widget.
        on_change: Callback function executed when page changes.
        args: Arguments to pass to the callback.
        kwargs: Keyword arguments to pass to the callback.
        disabled: Whether the widget is disabled.
        max_visible_pages: Maximum number of page buttons to display (excluding
            prev/next arrows). Set to None to show all pages (no truncation).
            Set to 0 to show only prev/next arrows.
        width: Widget width. "content": fit to content. "stretch": expand to
            container width. int: fixed pixel width.

    Returns:
        The currently selected page (1-indexed).

    Raises:
        StreamlitAPIException: If num_pages < 1, default is out of range,
            or max_visible_pages < 0.

    Example:

        ```python
        page = pagination(num_pages=10)
        st.write(f"Showing page {page}")
        ```
    """
    # Validate inputs
    if num_pages < 1:
        raise streamlit.errors.StreamlitAPIException(f"num_pages must be >= 1, got {num_pages}")
    if default < 1 or default > num_pages:
        raise streamlit.errors.StreamlitAPIException(f"default must be between 1 and {num_pages}, got {default}")
    if max_visible_pages is not None and max_visible_pages < 0:
        raise streamlit.errors.StreamlitAPIException(f"max_visible_pages must be >= 0 or None, got {max_visible_pages}")

    # Handle callback wrapper for on_change
    callback_fn = _on_page_change
    if on_change is not None:
        callback_args = args or ()
        callback_kwargs = kwargs or {}

        def wrapped_callback() -> None:
            on_change(*callback_args, **callback_kwargs)

        callback_fn = wrapped_callback

    component = _get_component()
    result = component(
        key=key,
        data={
            "num_pages": num_pages,
            "disabled": disabled,
            "max_visible_pages": max_visible_pages,
            "width": width,
        },
        default={"page": default},
        on_page_change=callback_fn,
    )

    # Get the current page from the result
    current_page: int = result.get("page", default)

    # Clamp the page if num_pages has decreased
    current_page = min(current_page, num_pages)

    return current_page


def example_interactive() -> None:
    """Interactive demo with configurable options."""
    st.write("### Interactive Demo")

    col1, col2 = st.columns(2)
    with col1:
        num_pages = st.number_input(
            "Number of pages",
            min_value=1,
            max_value=100,
            value=20,
            key="demo_num_pages",
        )
    with col2:
        max_visible = st.number_input(
            "Max visible pages",
            min_value=0,
            max_value=20,
            value=7,
            key="demo_max_visible",
            help="Set to 0 to show only arrows",
        )

    page = pagination(
        num_pages=num_pages,
        max_visible_pages=max_visible,
        key="interactive_pagination",
    )
    st.write(f"**Current page:** `{page}`")


def example_responsive() -> None:
    """Responsive pagination that adapts to container width."""
    st.write("### Responsive Behavior")
    st.write(
        "The pagination automatically adapts to container width with "
        "progressive degradation: full → current-only → arrows-only."
    )

    st.write("**Full width (stretch):**")
    page1 = pagination(
        num_pages=20,
        max_visible_pages=9,
        width="stretch",
        key="responsive_stretch",
    )
    st.write(f"Page: `{page1}`")

    st.write("**Fixed narrow width (150px) - shows current page only:**")
    page2 = pagination(
        num_pages=20,
        width=150,
        key="responsive_narrow",
    )
    st.write(f"Page: `{page2}`")

    st.write("**Very narrow (80px) - shows arrows only:**")
    page3 = pagination(
        num_pages=20,
        width=80,
        key="responsive_very_narrow",
    )
    st.write(f"Page: `{page3}`")


def example_with_data() -> None:
    """Paginating through data."""
    st.write("### Paginated Data")

    items = [f"Item {i}" for i in range(1, 101)]
    items_per_page = 10
    total_pages = (len(items) + items_per_page - 1) // items_per_page

    page = pagination(num_pages=total_pages, key="data_pagination")

    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))

    st.write(f"Showing items {start_idx + 1} - {end_idx} of {len(items)}")
    for item in items[start_idx:end_idx]:
        st.write(f"- {item}")


__title__ = "Pagination"
__desc__ = "A pagination widget for navigating through pages of content with numbered page buttons, prev/next arrows, and intelligent truncation."
__icon__ = "📄"
__examples__ = [
    example_interactive,
    example_responsive,
    example_with_data,
]
__author__ = "streamlit-extras"
__created_at__ = date(2026, 3, 24)
