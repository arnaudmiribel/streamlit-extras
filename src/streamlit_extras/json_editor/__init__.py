"""JSON Editor component for Streamlit.

An interactive JSON viewer/editor built with React and CCv2.
Uses @microlink/react-json-view for rendering and editing JSON data.
"""

from datetime import date
from functools import cache
from typing import Any, TypedDict, cast

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra


def _on_data_change() -> None:
    """Callback function for when the JSON data changes in the frontend."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.json_editor",
        js="index-*.js",
        html='<div class="react-root"></div>',
    )


class JsonEditorState(TypedDict):
    """State returned by the JSON editor component."""

    data: Any


@extra
def json_editor(
    data: dict | list | str,
    *,
    name: str | None = "root",
    collapsed: bool | int = False,
    theme: str | None = None,
    display_data_types: bool = True,
    display_object_size: bool = True,
    enable_clipboard: bool = True,
    sort_keys: bool = False,
    editable: bool = True,
    key: str | None = None,
) -> JsonEditorState:
    """Display an interactive JSON editor.

    A React-based component that renders JSON data with collapsible nodes
    and optional editing capabilities. When editing is enabled, users can
    add, edit, and delete keys/values.

    Args:
        data: The JSON data to display. Can be a dict, list, or JSON string.
        name: Label for the root node. Use None or False to hide.
        collapsed: Whether to collapse nodes by default.
            - False: Expand all nodes
            - True: Collapse all nodes
            - int: Collapse nodes at depth > int
        theme: Color theme for the viewer. If None (default), auto-detects
            based on whether the Streamlit theme is light or dark.
            Options include:
            "rjv-default", "monokai", "solarized", "ocean", "hopscotch",
            "summerfruit", "tomorrow", "ashes", "bespin", "brewer",
            "bright", "chalk", "codeschool", "colors", "eighties",
            "embers", "flat", "google", "grayscale", "greenscreen",
            "harmonic", "isotope", "marrakesh", "mocha", "ocean",
            "paraiso", "pop", "railscasts", "shapeshifter", "twilight"
        display_data_types: Show data type labels next to values.
        display_object_size: Show object/array item counts.
        enable_clipboard: Enable copy-to-clipboard functionality.
        sort_keys: Alphabetically sort object keys.
        editable: Enable add/edit/delete functionality.
        key: A unique key for this component instance.

    Returns:
        A TypedDict with a "data" key containing the current (possibly edited) JSON.

    Example:

        ```python
        result = json_editor({"name": "John", "age": 30}, key="my_editor")
        st.write("Current data:", result["data"])
        ```
    """
    # Parse JSON string if provided
    parsed_data: Any
    if isinstance(data, str):
        import json

        parsed_data = json.loads(data)
    else:
        parsed_data = data

    component = _get_component()
    return cast(
        "JsonEditorState",
        component(
            key=key,
            data={
                "json_data": parsed_data,
                "name": name,
                "collapsed": collapsed,
                "theme": theme or "",  # Empty string triggers auto-detect
                "display_data_types": display_data_types,
                "display_object_size": display_object_size,
                "enable_clipboard": enable_clipboard,
                "sort_keys": sort_keys,
                "editable": editable,
            },
            default={"data": parsed_data},
            on_data_change=_on_data_change,
        ),
    )


def example() -> None:
    """Example usage of the JSON editor component."""
    st.write("Edit the JSON below:")

    sample_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "active": True,
        "tags": ["developer", "python", "streamlit"],
        "address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "country": "USA",
        },
    }

    result = json_editor(
        sample_data,
        name="user",
        collapsed=False,
        editable=True,
        key="demo_editor",
    )

    st.write("**Current data:**")
    st.json(result["data"])


__title__ = "JSON Editor"
__desc__ = "An interactive JSON viewer/editor component built with React and CCv2."
__icon__ = "📝"
__examples__ = [example]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 3, 24)
