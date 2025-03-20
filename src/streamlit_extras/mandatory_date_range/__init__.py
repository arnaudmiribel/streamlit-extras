from datetime import date, timedelta
from typing import Any, Tuple, cast

import streamlit as st

from streamlit_extras import extra


@extra
def date_range_picker(
    label: str,
    error_message: str = "Please select start and end date",
    **kwargs: Any,
) -> Tuple[date, date]:
    """
    An extension of date_input. Working with date_input with a date range is
    frustrating becuase if you're assuming you will get a start and end date out of
    it, your code can break (not to mention your type hints), because if a user clicks
    on just one date, the app will go ahead and run with a single output. This widget
    enforces a start and end date being selected, and will stop the app if only one is chosen.

    Args:
        label (str): Label of the date widget
        error_message (str, optional): Error message when only one date is chosen.
            Defaults to "Please select start and end date".
        **kwargs (Any): Additional keyword arguments for `st.date_input`.

    Returns:
        Tuple[date, date]: Start and end date chosen in the widget
    """

    default_start = date.today() - timedelta(days=30)
    default_end = date.today()

    if "value" not in kwargs:
        kwargs["value"] = [default_start, default_end]
    else:
        if not isinstance(kwargs["value"], (list, tuple)):
            st.error(
                "date_range_picker requires a list or tuple"
                " so as to enable date range functionality"
            )
            st.stop()

    val = st.date_input(
        label=label,
        **kwargs,
    )
    try:
        start_date, end_date = cast(Tuple[date, date], val)
    except ValueError:
        st.error(error_message)
        st.stop()

    return start_date, end_date


def example():
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
__playground__ = True
