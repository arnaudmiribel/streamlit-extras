"""Shared utilities for CCv2 component registration.

This module provides helpers for Type D extras (CCv2 with dedicated files),
which store frontend assets in an `assets/` subdirectory.
"""

from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v2


def _load_asset(assets_dir: Path, filename: str) -> str:
    """Load a text file from the assets directory.

    Args:
        assets_dir: Path to the assets directory.
        filename: Name of the file to load.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = assets_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Component asset not found: {path}")
    return path.read_text(encoding="utf-8")


def register_file_component(
    name: str,
    package_dir: Path,
    *,
    html_file: str = "component.html",
    css_file: str | None = "component.css",
    js_file: str | None = "component.js",
    **kwargs: Any,
) -> Any:
    """Register a CCv2 component from files in the extra's assets/ directory.

    Loads file contents and passes them as inline strings to
    st.components.v2.component(). Returns the mount callable.

    Args:
        name: The component registration name (e.g. "streamlit_extras.radial_menu").
        package_dir: Path to the extra's package directory (typically Path(__file__).parent).
        html_file: Name of the HTML file in assets/. Defaults to "component.html".
        css_file: Name of the CSS file in assets/, or None to skip. Defaults to "component.css".
        js_file: Name of the JS file in assets/, or None to skip. Defaults to "component.js".
        **kwargs: Additional arguments passed to st.components.v2.component().

    Returns:
        The component mount callable from st.components.v2.component().

    Example:
        ```python
        from pathlib import Path
        from streamlit_extras._component_utils import register_file_component

        _COMPONENT = register_file_component(
            "streamlit_extras.my_extra",
            Path(__file__).parent,
        )
        ```
    """
    assets_dir = package_dir / "assets"
    html = _load_asset(assets_dir, html_file)
    css = _load_asset(assets_dir, css_file) if css_file else None
    js = _load_asset(assets_dir, js_file) if js_file else None

    return st.components.v2.component(name, html=html, css=css, js=js, **kwargs)
