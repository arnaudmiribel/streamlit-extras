from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import streamlit as st

from .. import extra

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


@extra
def bottom() -> DeltaGenerator:
    """Insert a multi-element container that sticks to the bottom of the app.

    Note that this can only be in the main body of the app, and not in
    other parts e.g. st.sidebar.

    Returns:
        DeltaGenerator: A container that sticks to the bottom of the app.

    Raises:
        Exception: If the bottom container is not supported in the Streamlit version.
    """
    if hasattr(st, "_bottom"):
        return st._bottom
    raise Exception("The bottom container is not supported in this Streamlit version.")


def example() -> None:
    st.write("This is the main container")

    with bottom():
        st.write("This is the bottom container")
        st.text_input("This is a text input in the bottom container")


__title__ = "Bottom Container"
__desc__ = "A multi-element container that sticks to the bottom of the app."
__icon__ = "⬇️"
__examples__ = [example]
__author__ = "Lukas Masuch"
__created_at__ = date(2024, 2, 27)
__experimental_playground__ = False
