"""Chart.js chart element for Streamlit.

Display charts using the Chart.js library with Streamlit theme integration.
Chart.js is known for its simplicity, lightweight footprint (~60KB gzipped),
and beautiful out-of-the-box charts with smooth animations.
"""

from datetime import date
from functools import cache
from typing import Any, Literal

import streamlit as st
import streamlit.components.v2
import streamlit.errors

from streamlit_extras import extra


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.chartjs_chart",
        js="index-*.js",
        html='<div class="react-root"></div>',
    )


@extra
def chartjs_chart(
    spec: dict[str, Any],
    *,
    height: Literal["content", "stretch"] | int = "content",
    theme: Literal["streamlit"] | None = "streamlit",
    key: str | None = None,
) -> None:
    """Display a chart using Chart.js.

    Chart.js is a popular JavaScript charting library known for its simplicity,
    performance, and smooth animations. This function renders a Chart.js chart
    from a configuration dictionary.

    Args:
        spec: Chart.js configuration object containing `type`, `data`, and optionally
            `options`. See Chart.js documentation for the full specification.
            Supported chart types: bar, line, pie, doughnut, radar, polarArea,
            bubble, scatter.
        height: Chart height. "content": fit to content (default). "stretch": fill
            container height. int: fixed pixel height.
        theme: Theme for the chart. "streamlit": use Streamlit theme colors for
            datasets, fonts, and grid (default). None: use Chart.js defaults.
        key: Unique key for this chart instance.

    Raises:
        StreamlitAPIException: If spec is not a dict or missing required fields.

    Example:
        ```python
        from streamlit_extras.chartjs_chart import chartjs_chart

        spec = {
            "type": "bar",
            "data": {
                "labels": ["January", "February", "March", "April", "May"],
                "datasets": [{"label": "Sales", "data": [65, 59, 80, 81, 56]}],
            },
        }
        chartjs_chart(spec)
        ```
    """
    # Validate spec is a dict
    if not isinstance(spec, dict):
        raise streamlit.errors.StreamlitAPIException(f"spec must be a dict, got {type(spec).__name__}")

    # Validate required spec fields
    if "type" not in spec:
        raise streamlit.errors.StreamlitAPIException(
            "spec must contain a 'type' field specifying the chart type (e.g., 'bar', 'line', 'pie')"
        )

    valid_types = {"bar", "line", "pie", "doughnut", "radar", "polarArea", "bubble", "scatter"}
    chart_type = spec.get("type")
    if chart_type not in valid_types:
        raise streamlit.errors.StreamlitAPIException(
            f"Invalid chart type '{chart_type}'. Valid types: {', '.join(sorted(valid_types))}"
        )

    if "data" not in spec:
        raise streamlit.errors.StreamlitAPIException("spec must contain a 'data' field with labels and datasets")

    component = _get_component()
    component(
        key=key,
        data={
            "spec": spec,
            "height": height,
            "theme": theme,
        },
        default=None,
    )


def example_bar_chart() -> None:
    """Basic bar chart example."""
    st.write("### Bar Chart")
    spec = {
        "type": "bar",
        "data": {
            "labels": ["January", "February", "March", "April", "May"],
            "datasets": [{"label": "Sales", "data": [65, 59, 80, 81, 56]}],
        },
    }
    chartjs_chart(spec)


def example_line_chart() -> None:
    """Multi-dataset line chart example."""
    st.write("### Line Chart")
    spec = {
        "type": "line",
        "data": {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "datasets": [
                {"label": "2024", "data": [10, 20, 15, 25]},
                {"label": "2025", "data": [15, 25, 20, 30]},
            ],
        },
        "options": {
            "plugins": {"title": {"display": True, "text": "Quarterly Revenue"}},
        },
    }
    chartjs_chart(spec)


def example_pie_chart() -> None:
    """Pie chart example."""
    st.write("### Pie Chart")
    spec = {
        "type": "pie",
        "data": {
            "labels": ["Red", "Blue", "Yellow", "Green"],
            "datasets": [{"data": [30, 25, 20, 25]}],
        },
    }
    chartjs_chart(spec)


def example_radar_chart() -> None:
    """Radar chart comparing multiple datasets."""
    st.write("### Radar Chart")
    spec = {
        "type": "radar",
        "data": {
            "labels": ["Speed", "Reliability", "Comfort", "Safety", "Efficiency"],
            "datasets": [
                {"label": "Car A", "data": [65, 59, 90, 81, 56]},
                {"label": "Car B", "data": [28, 48, 40, 19, 96]},
            ],
        },
    }
    chartjs_chart(spec)


def example_doughnut_chart() -> None:
    """Doughnut chart example."""
    st.write("### Doughnut Chart")
    spec = {
        "type": "doughnut",
        "data": {
            "labels": ["Desktop", "Mobile", "Tablet"],
            "datasets": [{"data": [55, 35, 10]}],
        },
        "options": {
            "plugins": {"title": {"display": True, "text": "Traffic by Device"}},
        },
    }
    chartjs_chart(spec)


__title__ = "Chart.js Chart"
__desc__ = "Display charts using the Chart.js library with Streamlit theme integration."
__icon__ = "📊"
__examples__ = [
    example_bar_chart,
    example_line_chart,
    example_pie_chart,
    example_radar_chart,
    example_doughnut_chart,
]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 4, 14)
