"""
Utilities for overriding Streamlit's global exception handler.

This module exposes a single function, `set_global_exception_handler`, which replaces
Streamlit's uncaught exception handler with a user-provided callable. It supports
Streamlit versions before and after 1.39.0, where the handler location changed.
"""

from __future__ import annotations

import sys
from typing import Callable

import streamlit as st
from packaging.version import Version

__all__ = ["set_global_exception_handler"]


def set_global_exception_handler(f: Callable) -> None:
    """Replace Streamlit's global uncaught exception handler with ``f``.

    Args:
        f (Callable): New exception handler function.

    Notes:
        - For Streamlit versions earlier than 1.39.0, the handler lives under
          ``streamlit.runtime.scriptrunner.script_runner``.
        - For Streamlit 1.39.0 and later, it resides under ``streamlit.error_util``.
    """

    if Version(st.__version__) < Version("1.39.0"):
        parent_module = sys.modules["streamlit.runtime.scriptrunner.script_runner"]
    else:
        parent_module = sys.modules["streamlit.error_util"]

    parent_module.handle_uncaught_app_exception.__code__ = f.__code__
