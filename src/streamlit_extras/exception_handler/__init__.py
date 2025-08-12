"""
Override Streamlit's global uncaught exception handler.

This extra exposes a single function, ``set_global_exception_handler``, that replaces
Streamlit's uncaught exception handler with a user-provided callable. It supports
Streamlit versions before and after 1.39.0, where the handler location changed.
"""

from __future__ import annotations

import sys
from typing import Callable

import streamlit as st
from packaging.version import Version

from .. import extra

__all__ = ["set_global_exception_handler"]


@extra
def set_global_exception_handler(f: Callable) -> None:
    """Replace Streamlit's global uncaught exception handler with ``f``.

    Args:
        f (Callable): New exception handler function.

    Notes:
        - For Streamlit versions earlier than 1.39.0, the handler lives under
          ``streamlit.runtime.scriptrunner.script_runner``.
        - For Streamlit 1.39.0 and later, it resides under ``streamlit.error_util``.

    Warning:
        This function mutates Streamlit internals. Use carefully and test thoroughly.
    """

    if Version(st.__version__) < Version("1.39.0"):
        parent_module = sys.modules["streamlit.runtime.scriptrunner.script_runner"]
    else:
        parent_module = sys.modules["streamlit.error_util"]

    parent_module.handle_uncaught_app_exception.__code__ = f.__code__


def example() -> None:
    """Demonstrate installing a custom handler and triggering an exception.

    Includes a sample handler that logs context and still surfaces the exception to the user.
    """
    import traceback
    from datetime import datetime

    st.write(
        "Install a custom handler that logs context and shows the exception to the user."
    )

    def custom_exception_handler(exception: Exception) -> None:
        """Custom handler that logs exception data and sends notifications.

        You can customize the logging destination and notification methods.
        """

        # Still show the exception to the user (default behavior)
        st.exception(exception)

        # Collect context about the exception
        exception_data = {
            "exception_name": str(exception),
            "traceback": str(traceback.format_exc()).strip(),
            "user_name": (
                getattr(st.user, "user_name", "unknown")
                if hasattr(st, "user")
                else "unknown"
            ),
            "timestamp": datetime.now().isoformat(),
            "app_name": "your_app_name",  # Replace with real app identification
            "page_name": "current_page",  # Replace with real page identification
        }

        # Log the exception (choose your method)
        st.toast(exception_data)

    if st.button("Install custom handler"):
        set_global_exception_handler(custom_exception_handler)
        st.success("Custom handler installed for this app run.")

    if st.button("Trigger an exception"):
        raise RuntimeError("Boom! This is a demo exception.")


__title__ = "Exception Handler"
__desc__ = (
    "Override Streamlit's uncaught exception handler to customize error display and"
    " logging."
)
__icon__ = "🛡️"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__playground__ = False
