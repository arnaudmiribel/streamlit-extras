from contextlib import contextmanager
from typing import Generator, Sequence

import numpy as np
import pandas as pd
import streamlit as st

from .. import extra


@st.experimental_memo
def to_csv(data: pd.DataFrame):
    return data.to_csv().encode("utf-8")


@extra  # type: ignore
@contextmanager
def chart_container(
    data: pd.DataFrame,
    tabs: Sequence[str] = (
        "Chart 📈",
        "Dataframe 📄",
        "Export 📁",
    ),
) -> Generator:
    """Embed chart in a (chart, data, export) tabs container to let the viewer explore and export its underlying data.

    Args:
        data (pd.DataFrame): Dataframe used in the dataframe tab.
        tabs (Iterable, optional): Tab labels. Defaults to ("Chart 📈", "Dataframe 📄", "Export 📁").
    """

    tab_1, tab_2, tab_3 = st.tabs(tabs)

    with tab_1:
        yield

    with tab_2:
        st.dataframe(data, use_container_width=True)

    with tab_3:
        st.download_button(
            "Download data as .csv",
            data=to_csv(data),
            file_name="data.csv",
            mime="text/csv",
            # In case there are multiple containers created, this ensures
            # the buttons will have a different key even if the label is the same.
            key=np.random.randint(0, 1e9),
        )


def example_one():
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    with chart_container(chart_data):
        st.write("Here's a cool chart")
        st.area_chart(chart_data)


def example_two():
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    with chart_container(chart_data):
        st.write(
            "I can use a subset of the data for my chart... "
            "but still give all the necessary context in "
            "`chart_container`!"
        )
        st.area_chart(chart_data[["a", "b"]])


__title__ = "Chart container"
__desc__ = "Embed your chart in a nice tabs container to let viewers explore and export its underlying data."
__icon__ = "🖼️"
__examples__ = [example_one, example_two]
__author__ = "Arnaud Miribel"
