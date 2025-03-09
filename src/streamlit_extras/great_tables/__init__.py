from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import streamlit as st

from .. import extra

if TYPE_CHECKING:
    from great_tables import GT


@extra
def great_tables(
    table: "GT", width: int | Literal["stretch", "content"] = "stretch"
) -> None:
    """
    Render a Great Tables object in Streamlit.

    Args:
        table: A Great Tables object.
        width: The width of the table. One of:
            - `stretch` (default): Stretch the table to the width of the container.
            - `int`: The width of the table in pixels.
    """
    if width == "stretch":
        table = table.tab_options(container_width="100%", table_width="100%")
    elif width == "content":
        # Do nothing -> uses content as default.
        pass
    else:
        table = table.tab_options(
            container_width=f"{width}px", table_width=f"{width}px"
        )

    # TODO(lukasmasuch): Apply more modifications to make it look better with Streamlit.
    # https://posit-dev.github.io/great-tables/reference/GT.tab_options.html#great_tables.GT.tab_options
    st.html(table.as_raw_html())


def example():
    try:
        from great_tables import GT
        from great_tables.data import sp500

        # Define the start and end dates for the data range
        start_date = "2010-06-07"
        end_date = "2010-06-14"

        # Filter sp500 using Pandas to dates between `start_date` and `end_date`
        sp500_mini = sp500[(sp500["date"] >= start_date) & (sp500["date"] <= end_date)]

        # Create a display table based on the `sp500_mini` table data
        table = (
            GT(sp500_mini)
            .tab_header(title="S&P 500", subtitle=f"{start_date} to {end_date}")
            .fmt_currency(columns=["open", "high", "low", "close"])
            .fmt_date(columns="date", date_style="wd_m_day_year")
            .fmt_number(columns="volume", compact=True)
            .cols_hide(columns="adj_close")
        )

        great_tables(table, width="stretch")
    except ImportError:
        st.warning(
            "This example requires the `great_tables` package. "
            "Install it with `pip install great-tables`."
        )


__title__ = "Great Tables"
__desc__ = """Render [Great Tables](https://posit-dev.github.io/great-tables/articles/intro.html) objects in Streamlit.
Great tables allows to implement wonderful-looking display tables in Python.
"""
__icon__ = "🧮"
__examples__ = [example]
__author__ = "Lukas Masuch"
__playground__ = False
