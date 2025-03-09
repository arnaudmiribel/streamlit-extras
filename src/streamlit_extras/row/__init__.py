from __future__ import annotations

from typing import Literal, Optional, Sequence, Union

import numpy as np
import pandas as pd
import streamlit as st

from streamlit_extras import grid

from .. import extra

SpecType = Union[int, Sequence[Union[int, float]]]


@extra
def row(
    spec: SpecType,
    gap: Optional[str] = "small",
    vertical_align: Literal["top", "center", "bottom"] = "top",
) -> grid.GridDeltaGenerator:
    """
    Insert a multi-element, horizontal container into your app.

    This function inserts a container into your app that can hold
    a number of elements as defined in the provided spec. Elements can be added
    to the returned container by calling methods directly on the returned object.

    Args:
        spec (SpecType): Controls the number and width of cells to insert in the row. Can be one of:
            * An integer specifying the number of cells. All cells will have equal
            width in this case.
            * An iterable of numbers (int or float) that specifies the relative width of
            each cell. For instance, ``[0.7, 0.3]`` creates two cells where the first
            one occupies 70% of the available width, and the second one occupies 30%.
            Or, ``[1, 2, 3]`` creates three cells where the second one is twice
            as wide as the first one, and the third one is three times that width.
        gap (Optional[str], optional): "small", "medium", or "large"
            The size of the gap between cells, can be "small", "medium", or "large".
            This parameter specifies the visual space between the elements within the row.
            Defaults to "small".
        vertical_align (Literal["top", "center", "bottom"], optional): The vertical alignment
            of the cells in the row. It can be either "top", "center", or "bottom", aligning
            the contents of each cell accordingly. Defaults to "top".

    Returns:
        grid.GridDeltaGenerator: RowContainer
            A row container object. Elements can be added to this row by calling methods directly
            on the returned object.
    """
    container = st.container()

    return grid.GridDeltaGenerator(
        parent_dg=container, spec=[spec], gap=gap, vertical_align=vertical_align
    )


def example():
    random_df = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

    row1 = row(2, vertical_align="center")
    row1.dataframe(random_df, use_container_width=True)
    row1.line_chart(random_df, use_container_width=True)

    row2 = row([2, 4, 1], vertical_align="bottom")

    row2.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
    row2.text_input("Your name")
    row2.button("Send", use_container_width=True)


__title__ = "Row Layout"
__desc__ = "A multi-element horizontal container that places elements in a row."
__icon__ = "🟰"
__examples__ = [example]
__author__ = "Lukas Masuch"
__playground__ = True
