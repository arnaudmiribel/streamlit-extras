from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import streamlit as st

from .. import extra

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


@extra
def skeleton(height: int | None = None) -> DeltaGenerator:
    """Insert a single-element container which displays a "skeleton" placeholder.

    Inserts a container into your app that can be used to hold a single element.
    This allows you to, for example, remove elements at any point, or replace
    several elements at once (using a child multi-element container).

    To insert/replace/clear an element on the returned container, you can
    use ``with`` notation or just call methods directly on the returned object.

    Args:
        height (int | None): Desired height of the skeleton expressed in pixels.
            If None, a default height is used.

    Returns:
        DeltaGenerator: A container that displays a skeleton placeholder.

    Raises:
        Exception: If the skeleton container is not supported in the Streamlit version.
    """
    if hasattr(st._main, "_skeleton"):
        return st._main._skeleton(height=height)
    raise Exception("The skeleton container is not supported in this Streamlit version.")


def example() -> None:
    st.write("This is the main container")

    # Example 1: Basic usage
    skeleton_container = skeleton()
    tall_skeleton = skeleton(height=200)

    if st.button("Fill skeleton container"):
        skeleton_container.write("This is content in the skeleton container")
        tall_skeleton.dataframe(
            {
                "A": [1, 2, 3],
                "B": [4, 5, 6],
            }
        )


__title__ = "Skeleton Placeholder"
__desc__ = "A single-element container which displays a skeleton placeholder."
__icon__ = "🦴"
__examples__ = [example]
__author__ = "Lukas Masuch"
__created_at__ = date(2025, 3, 10)
__playground__ = True
