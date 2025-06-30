"""
Altex integration for streamlit-extras.

This module provides a bridge to the standalone altex package,
decorating all chart functions with @extra for streamlit-extras framework.
"""

import functools
from typing import Any, Callable

import altair as alt
import altex
import pandas as pd
import streamlit as st

try:
    from streamlit import cache_data  # streamlit >= 1.18.0
except ImportError:
    from streamlit import experimental_memo as cache_data  # streamlit >= 0.89

from .. import extra


def _wrap_with_extra(func: Callable) -> Callable:
    """Wrap an altex function with the @extra decorator."""

    @extra
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper


# Chart functions from altex, wrapped with @extra
line_chart = _wrap_with_extra(altex.line_chart)
bar_chart = _wrap_with_extra(altex.bar_chart)
area_chart = _wrap_with_extra(altex.area_chart)
scatter_chart = _wrap_with_extra(altex.scatter_chart)
histogram = _wrap_with_extra(altex.histogram)
sparkline = _wrap_with_extra(altex.sparkline)
sparkbar = _wrap_with_extra(altex.sparkbar)
sparkarea = _wrap_with_extra(altex.sparkarea)

# Data utilities (re-exported as-is)
get_stocks_data = altex.get_stocks_data
get_weather_data = altex.get_weather_data
get_barley_data = altex.get_barley_data
get_random_data = altex.get_random_data


# Examples for streamlit-extras gallery
@cache_data
def example_line():
    stocks = get_stocks_data()

    line_chart(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful simple line chart",
    )


@cache_data
def example_multi_line():
    stocks = get_stocks_data()
    line_chart(
        data=stocks,
        x="date",
        y="price",
        color="symbol",
        title="A beautiful multi line chart",
    )


@cache_data
def example_bar():
    stocks = get_stocks_data()
    bar_chart(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful bar chart",
    )


@cache_data
def example_hist():
    stocks = get_stocks_data()
    histogram(
        data=stocks.assign(price=stocks.price.round(0)),
        x="price",
        title="A beautiful histogram",
    )


@cache_data
def example_scatter_opacity():
    weather = get_weather_data()
    scatter_chart(
        data=weather,
        x=alt.X("wind:Q", title="Custom X title"),
        y=alt.Y("temp_min:Q", title="Custom Y title"),
        title="A beautiful scatter chart with custom opacity",
        opacity=0.2,
    )


@cache_data
def example_bar_horizontal():
    weather = get_weather_data()
    bar_chart(
        data=weather.head(15),
        x="temp_max:Q",
        y=alt.Y("date:O", title="Temperature"),
        title="A beautiful horizontal bar chart",
    )


@cache_data
def example_bar_log():
    weather = get_weather_data()
    bar_chart(
        data=weather,
        x=alt.X("temp_max:Q", title="Temperature"),
        y=alt.Y(
            "count()",
            title="Count of records",
            scale=alt.Scale(type="symlog"),
        ),
        title="A beautiful histogram... with log scale",
    )


@cache_data
def example_bar_sorted():
    weather = get_weather_data()
    bar_chart(
        data=weather.sort_values(by="temp_max", ascending=False).head(25),
        x=alt.X("date", sort="-y"),
        y=alt.Y("temp_max:Q"),
        title="A beautiful sorted-by-value bar chart",
    )


@cache_data
def example_scatter():
    weather = get_weather_data()
    scatter_chart(
        data=weather,
        x=alt.X("wind:Q", title="Custom X title"),
        y=alt.Y("temp_min:Q", title="Custom Y title"),
        title="A beautiful scatter chart",
    )


@cache_data
def example_hist_time():
    weather = get_weather_data()
    histogram(
        data=weather,
        x="week(date):T",
        y="day(date):T",
        color=alt.Color(
            "median(temp_max):Q",
            legend=None,
        ),
        title="A beautiful time hist chart",
    )


@cache_data
def example_sparkline():
    stocks = get_stocks_data()
    sparkline(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful sparkline chart",
    )


@cache_data
def example_minisparklines():
    stocks = get_stocks_data()

    left, middle, right = st.columns(3)
    with left:
        data = stocks.query("symbol == 'GOOG'")
        st.metric("GOOG", int(data["price"].mean()))
        sparkline(
            data=data,
            x="date",
            y="price:Q",
        )
    with middle:
        data = stocks.query("symbol == 'MSFT'")
        st.metric("MSFT", int(data["price"].mean()))
        sparkline(
            data=data,
            x="date",
            y="price:Q",
        )
    with right:
        data = stocks.query("symbol == 'AAPL'")
        st.metric("AAPL", int(data["price"].mean()))
        sparkline(
            data=data,
            x="date",
            y="price:Q",
        )


@cache_data
def example_sparkbar():
    stocks = get_stocks_data()
    sparkbar(
        data=stocks.query("symbol == 'GOOG'"),
        x="date",
        y="price",
        title="A beautiful sparkbar chart",
    )


@cache_data
def example_sparkarea():
    random_data = get_random_data()
    df = pd.melt(
        random_data,
        id_vars="index",
        value_vars=list("abcdefg"),
    )

    sparkarea(
        data=df,
        x="index",
        y="value",
        color=alt.Color("variable", legend=None),
        title="A beautiful (also probably useless) sparkarea chart",
        opacity=alt.value(0.6),
    )


@cache_data
def example_bar_stacked():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x=alt.X("variety", title="Variety"),
        y="sum(yield)",
        color="site",
        title="A beautiful stacked bar chart",
    )


@cache_data
def example_bar_normalized():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x=alt.X("variety:N", title="Variety"),
        y=alt.Y("sum(yield):Q", stack="normalize"),
        color="site:N",
        title="A beautiful normalized stacked bar chart",
    )


@cache_data
def example_bar_normalized_custom():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x=alt.X("variety", title="Variety"),
        y="sum(yield)",
        color=alt.Color("site", scale=alt.Scale(scheme="lighttealblue"), legend=None),
        title="A beautiful stacked bar chart (without legend, custom colors)",
    )


@cache_data
def example_bar_grouped():
    barley = get_barley_data()
    bar_chart(
        data=barley,
        x="year:O",
        y="sum(yield):Q",
        color="year:N",
        column="site:N",
        title="A beautiful grouped bar charts",
        width=90,
        use_container_width=False,
    )


# For streamlit-extras framework compatibility
__funcs__ = [
    "line_chart",
    "bar_chart",
    "area_chart",
    "scatter_chart",
    "histogram",
    "sparkline",
    "sparkbar",
    "sparkarea",
]

# Streamlit-extras metadata
__title__ = "Altex"
__desc__ = (
    "A simple wrapper on top of Altair to make Streamlit charts in an"
    " express API. If you're lazy and/or familiar with Altair, this is "
    " probably a good fit! Inspired by plost and plotly-express."
)
__icon__ = "👸"
__examples__ = {
    example_line: [line_chart, get_stocks_data],
    example_multi_line: [line_chart, get_stocks_data],
    example_bar: [bar_chart, get_stocks_data],
    example_hist: [histogram, get_stocks_data],
    example_scatter: [scatter_chart, get_weather_data],
    example_sparkline: [sparkline, get_stocks_data],
    example_minisparklines: [sparkline, get_stocks_data],
    example_sparkbar: [sparkbar, get_stocks_data],
    example_sparkarea: [sparkarea, get_random_data],
    example_hist_time: [histogram, get_weather_data],
    example_bar_sorted: [bar_chart, get_weather_data],
    example_bar_normalized: [bar_chart, get_barley_data],
    example_bar_grouped: [bar_chart, get_barley_data],
    example_bar_horizontal: [bar_chart, get_weather_data],
    example_bar_log: [bar_chart, get_weather_data],
    example_scatter_opacity: [scatter_chart, get_weather_data],
    example_bar_normalized_custom: [bar_chart, get_barley_data],
}
__author__ = "Arnaud Miribel"
__playground__ = False
__stlite__ = False
