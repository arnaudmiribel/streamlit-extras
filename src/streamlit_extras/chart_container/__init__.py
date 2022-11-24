from contextlib import contextmanager
from typing import Generator, Sequence

import numpy as np
import pandas as pd
import streamlit as st

from .. import extra

# from ..no_default_selectbox import selectbox


@st.experimental_memo
def _to_csv(data: pd.DataFrame):
    return data.to_csv().encode("utf-8")


@st.experimental_memo
def _to_excel(data: pd.DataFrame):
    return data.to_excel().encode("utf-8")


@st.experimental_memo
def _to_parquet(data: pd.DataFrame):
    return data.to_parquet()


@st.experimental_memo
def _get_supported_exports():
    return {
        "CSV": {
            "function": _to_csv,
            "extension": ".csv",
            "mime": "text/csv",
        },
        "Excel": {
            "function": _to_excel,
            "extension": ".xlsx",
            "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
        "Parquet": {
            "function": _to_parquet,
            "extension": ".parquet",
        },
    }


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
        if len(data) > 1_000_000:
            st.warning(
                f"Dataframe has {len(data)} rows. Truncating to 1M rows for export."
            )

        export_data = data.head(1_000_000)
        supported_exports = _get_supported_exports()
        chosen_export_format = st.selectbox(
            "Choose export format",
            supported_exports.keys(),
            key=f"export_{np.random.randint(0, 1e9)}",
        )

        if chosen_export_format:
            export_utils = supported_exports[chosen_export_format]
            exporter = export_utils["function"]
            extension = export_utils["extension"]
            st.download_button(
                f"Download data as {extension}",
                data=exporter(export_data),
                file_name="data" + extension,
                mime=export_utils.get("mime"),
                key=f"export_button_{np.random.randint(0, 1e9)}",
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
