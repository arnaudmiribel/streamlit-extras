from contextlib import contextmanager
from typing import Generator, Sequence

import numpy as np
import pandas as pd
import streamlit as st

try:
    from streamlit import cache_data  # streamlit >= 1.18.0
except ImportError:
    from streamlit import experimental_memo as cache_data  # streamlit >= 0.89

from .. import extra


@cache_data
def _to_csv(data: pd.DataFrame):
    return data.to_csv().encode("utf-8")


@cache_data
def _to_parquet(data: pd.DataFrame):
    return data.to_parquet()


_SUPPORTED_EXPORTS = {
    "CSV": {
        "function": _to_csv,
        "extension": ".csv",
        "mime": "text/csv",
    },
    "Parquet": {
        "function": _to_parquet,
        "extension": ".parquet",
    },
}

_SUPPORTED_EXPORT_KEYS = list(_SUPPORTED_EXPORTS.keys())


@extra  # type: ignore
@contextmanager
def chart_container(
    data: pd.DataFrame,
    tabs: Sequence[str] = (
        "Chart 📈",
        "Dataframe 📄",
        "Export 📁",
    ),
    export_formats: Sequence[str] = _SUPPORTED_EXPORT_KEYS,
) -> Generator:
    """Embed chart in a (chart, data, export, explore) tabs container to let the viewer explore and export its underlying data.

    Args:
        data (pd.DataFrame): Dataframe used in the dataframe tab.
        tabs (Sequence, optional): Tab labels. Defaults to ("Chart 📈", "Dataframe 📄", "Export 📁").
        export_formats (Sequence, optional): Export file formats. Defaults to ("CSV", "Parquet")
    """

    assert all(
        export_format in _SUPPORTED_EXPORTS for export_format in export_formats
    ), (
        f"Input format is not supported, please use one within {_SUPPORTED_EXPORTS.keys()}"
    )

    if "chart_container_widget_key" not in st.session_state:
        st.session_state["chart_container_widget_key"] = 0

    def _get_random_widget_key() -> int:
        st.session_state.chart_container_widget_key += 1
        return st.session_state.chart_container_widget_key

    tab_1, tab_2, tab_3 = st.tabs(tabs)

    with tab_1:
        yield

    with tab_2:
        st.dataframe(data, use_container_width=True)

    with tab_3:
        st.caption("Export limited to 1 million rows.")
        export_data = data.head(1_000_000)
        for chosen_export_format in export_formats:
            export_utils = _SUPPORTED_EXPORTS[chosen_export_format]
            exporter = export_utils["function"]
            extension = export_utils["extension"]
            st.download_button(
                f"Download data as {extension}",
                data=exporter(export_data),
                file_name="data" + extension,
                mime=export_utils.get("mime"),
                key=f"chart_container_download_{_get_random_widget_key()}",
            )


def get_random_data():
    np.random.seed(42)
    return pd.DataFrame(np.random.randn(20, 3), columns=list("abc"))


def example_one():
    chart_data = get_random_data()
    with chart_container(chart_data):
        st.write("Here's a cool chart")
        st.area_chart(chart_data)


def example_two():
    chart_data = get_random_data()
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
__examples__ = [
    example_one,
    example_two,
]
__author__ = "Arnaud Miribel"
__playground__ = True
