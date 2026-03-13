"""Compatibility helpers for Streamlit version requirements."""

import streamlit as st


def require_ccv2() -> None:
    """Verify that the current Streamlit version supports Custom Components v2.

    Raises:
        ImportError: If Streamlit version does not support CCv2.
    """
    if not hasattr(st.components, "v2"):
        raise ImportError(
            "Custom Components v2 requires Streamlit >= 1.46.0. "
            f"Current version: {st.__version__}"
        )
