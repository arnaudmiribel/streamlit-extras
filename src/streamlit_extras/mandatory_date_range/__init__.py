from datetime import date, timedelta
from typing import Any, cast

import streamlit as st

from streamlit_extras import extra


@extra
def date_range_picker(
    title: str,
    default_start: date | None = None,
    default_end: date | None = None,
    min_date: date | None = None,
    max_date: date | None = None,
    error_message: str = "Please select start and end date",
    **kwargs: Any,
) -> tuple[date, date]:
    """
    Working with date_input with a date range is frustrating becuase if you're
    assuming you will get a start and end date out of it, your code can break (not
    to mention your type hints), because if a user clicks on just one date, the app
    will go ahead and run with a single output. This widget enforces a start and
    end date being selected, and will stop the app if only one is chosen.

    Args:
        title (str): Title of the date widget
        default_start (Optional[date], optional): Default start date. Defaults to None.
        default_end (Optional[date], optional): Default end date. Defaults to None.
        min_date (Optional[date], optional): Minimum date. Defaults to None.
        max_date (Optional[date], optional): Maximum date. Defaults to None.
        error_message (str, optional): Error message when only one date is chosen.
            Defaults to "Please select start and end date".
        **kwargs (Any): Additional keyword arguments for `st.date_input`.

    Returns:
        Tuple[date, date]: Start and end date chosen in the widget
    """

    if default_start is None:
        default_start = date.today() - timedelta(days=30)
    if default_end is None:
        default_end = date.today()

    val = st.date_input(
        title,
        value=[default_start, default_end],
        min_value=min_date,
        max_value=max_date,
        **kwargs,
    )
    try:
        start_date, end_date = cast("tuple[date, date]", val)
    except ValueError:
        st.error(error_message)
        st.stop()

    return start_date, end_date


def example() -> None:
    st.write(
        """
        This is an example of a date range picker that *always* returns a start and
        end date, even if the user has only selected one of the dates. Until the
        user selects both dates, the app will not run.
        """
    )
    result = date_range_picker("Select a date range")
    st.write("Result:", result)


st.date_input
__title__ = "Mandatory Date Range Picker"
__desc__ = """
Just like st.date_input, but enforces that it always and only returns a start and
end date, even if the user has only selected one of the dates. Until the user
selects both dates, the app will not run.
"""
__icon__ = "📅"
__examples__ = [example]
__author__ = "Mohammad Junaid"
__created_at__ = date(2022, 11, 18)
__playground__ = True
