"""Dataframe Filter component for Streamlit.

A filter bar widget that provides an intuitive UI for filtering pandas DataFrames.
Built with React and CCv2, inspired by modern data table filter UIs.
"""

from __future__ import annotations

from functools import cache
from typing import Any, Literal, TypedDict, cast

import pandas as pd
import streamlit as st
import streamlit.components.v2
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from streamlit_extras import extra

ColumnType = Literal["text", "number", "date", "boolean", "option"]


class ColumnConfig(TypedDict):
    """Configuration for a filterable column."""

    id: str
    name: str
    type: ColumnType
    options: list[str] | None


class FilterCondition(TypedDict):
    """A single filter condition."""

    column: str
    operator: str
    value: Any


class DataframeFilterState(TypedDict):
    """State returned by the dataframe filter component."""

    filters: list[FilterCondition]


def _on_filters_change() -> None:
    """Callback function for when filters change in the frontend."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.dataframe_filter",
        js="index-*.js",
        css="index-*.css",
        html='<div class="react-root"></div>',
    )


def _infer_column_type(series: pd.Series) -> ColumnType:
    """Infer the filter type for a pandas Series.

    Args:
        series: The pandas Series to analyze.

    Returns:
        The inferred column type.
    """
    if is_bool_dtype(series):
        return "boolean"
    if is_datetime64_any_dtype(series):
        return "date"
    if is_numeric_dtype(series):
        return "number"
    # Treat columns with few unique values as categorical/option
    if series.nunique() <= 10 or isinstance(series.dtype, pd.CategoricalDtype):
        return "option"
    return "text"


def _get_column_options(series: pd.Series) -> list[str] | None:
    """Get the unique values for an option-type column.

    Args:
        series: The pandas Series to analyze.

    Returns:
        List of unique string values, or None if not an option type.
    """
    if series.nunique() <= 10 or isinstance(series.dtype, pd.CategoricalDtype):
        # Convert to strings and sort
        options = [str(v) for v in series.dropna().unique()]
        options.sort()
        return options
    return None


def _build_columns_config(
    df: pd.DataFrame,
    columns: list[str] | None,
) -> list[ColumnConfig]:
    """Build column configuration from DataFrame schema.

    Args:
        df: The pandas DataFrame.
        columns: Optional list of columns to include.

    Returns:
        List of column configurations.
    """
    cols_to_include = columns if columns is not None else list(df.columns)

    configs: list[ColumnConfig] = []
    for col in cols_to_include:
        if col not in df.columns:
            continue

        series = df[col]
        col_type = _infer_column_type(series)
        options = _get_column_options(series) if col_type == "option" else None

        configs.append(
            {
                "id": col,
                "name": col,
                "type": col_type,
                "options": options,
            }
        )

    return configs


def _has_valid_value(operator: str, value: Any) -> bool:
    """Check if a filter has a valid value to apply.

    Args:
        operator: The filter operator.
        value: The filter value.

    Returns:
        True if the filter should be applied, False to skip it.
    """
    # Operators that don't require a value
    no_value_operators = {"is_empty", "is_not_empty", "is_true", "is_false"}
    if operator in no_value_operators:
        return True

    # Check for empty values
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, list):
        # For "between" operator, both values must be non-empty
        if operator == "between":
            return len(value) == 2 and all(
                v is not None and str(v).strip() for v in value
            )
        # For multi-select operators, at least one value must be selected
        return len(value) > 0

    return True


def _apply_filters(
    df: pd.DataFrame,
    filters: list[FilterCondition],
) -> pd.DataFrame:
    """Apply filter conditions to a DataFrame.

    Args:
        df: The pandas DataFrame to filter.
        filters: List of filter conditions.

    Returns:
        The filtered DataFrame.
    """
    result = df.copy()

    for f in filters:
        column = f["column"]
        operator = f["operator"]
        value = f["value"]

        if column not in result.columns:
            continue

        # Skip filters without valid values
        if not _has_valid_value(operator, value):
            continue

        series = result[column]

        try:
            if operator == "contains":
                mask = series.astype(str).str.contains(str(value), case=False, na=False)
            elif operator == "not_contains":
                mask = ~series.astype(str).str.contains(str(value), case=False, na=False)
            elif operator == "equals":
                if is_numeric_dtype(series):  # noqa: SIM108
                    mask = series == float(value)  # noqa: RUF069
                else:
                    mask = series.astype(str) == str(value)
            elif operator == "not_equals":
                if is_numeric_dtype(series):  # noqa: SIM108
                    mask = series != float(value)  # noqa: RUF069
                else:
                    mask = series.astype(str) != str(value)
            elif operator == "starts_with":
                mask = series.astype(str).str.startswith(str(value), na=False)
            elif operator == "ends_with":
                mask = series.astype(str).str.endswith(str(value), na=False)
            elif operator == "greater_than":
                mask = series > float(value)
            elif operator == "greater_than_or_equal":
                mask = series >= float(value)
            elif operator == "less_than":
                mask = series < float(value)
            elif operator == "less_than_or_equal":
                mask = series <= float(value)
            elif operator == "between":
                if isinstance(value, list) and len(value) == 2:
                    if is_datetime64_any_dtype(series):
                        date_min = pd.to_datetime(value[0])
                        date_max = pd.to_datetime(value[1])
                        mask = series.between(date_min, date_max)
                    else:
                        num_min = float(value[0])
                        num_max = float(value[1])
                        mask = series.between(num_min, num_max)
                else:
                    continue
            elif operator == "is_empty":
                mask = series.isna() | (series.astype(str).str.len() == 0)
            elif operator == "is_not_empty":
                mask = ~(series.isna() | (series.astype(str).str.len() == 0))
            elif operator == "is_any_of":
                if isinstance(value, list):
                    mask = series.astype(str).isin([str(v) for v in value])
                else:
                    continue
            elif operator == "is_none_of":
                if isinstance(value, list):
                    mask = ~series.astype(str).isin([str(v) for v in value])
                else:
                    continue
            elif operator == "before":
                date_val = pd.to_datetime(value)
                mask = series < date_val
            elif operator == "after":
                date_val = pd.to_datetime(value)
                mask = series > date_val
            elif operator == "is_true":
                mask = series == True  # noqa: E712
            elif operator == "is_false":
                mask = series == False  # noqa: E712
            else:
                continue

            result = result[mask]
        except (ValueError, TypeError):
            # Skip invalid filter conditions
            continue

    return result


@extra
def dataframe_filter(
    df: pd.DataFrame,
    *,
    columns: list[str] | None = None,
    key: str | None = None,
) -> pd.DataFrame:
    """Display a filter bar for the given DataFrame.

    A React-based component that provides an intuitive filter UI for pandas
    DataFrames. Users can add multiple filter conditions based on column
    data types with operators like contains, equals, greater than, between, etc.

    Args:
        df: The pandas DataFrame to filter.
        columns: Optional list of column names to allow filtering.
            If None, all columns are filterable.
        key: A unique key for this component instance.

    Returns:
        The filtered DataFrame based on user-selected filters.

    Example:
        >>> filtered_df = dataframe_filter(df, key="my_filter")
        >>> st.dataframe(filtered_df)
    """
    # Build column configuration from DataFrame schema
    columns_config = _build_columns_config(df, columns)

    if not columns_config:
        st.warning("No filterable columns found in the DataFrame.")
        return df

    component = _get_component()
    state = cast(
        "DataframeFilterState",
        component(
            key=key,
            data={
                "columns": columns_config,
            },
            default={"filters": []},
            on_filters_change=_on_filters_change,
        ),
    )

    # Apply filters to the DataFrame
    filters = state.get("filters", [])
    if filters:
        return _apply_filters(df, filters)

    return df


def example() -> None:
    """Example usage of the dataframe filter component."""
    # Create sample data
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"],
            "age": [25, 30, 35, 28, 22, 45],
            "status": ["Active", "Inactive", "Active", "Active", "Inactive", "Active"],
            "salary": [50000, 60000, 75000, 55000, 45000, 90000],
            "joined": pd.to_datetime(
                [
                    "2020-01-15",
                    "2019-06-20",
                    "2021-03-10",
                    "2022-08-05",
                    "2023-01-01",
                    "2018-11-30",
                ]
            ),
        }
    )

    st.write("Filter the employee data:")
    filtered_df = dataframe_filter(df, key="employee_filter")

    st.dataframe(filtered_df)
    st.caption(f"Showing {len(filtered_df)} of {len(df)} rows")


__title__ = "Dataframe Filter"
__desc__ = "A filter bar widget for filtering pandas DataFrames with an intuitive UI."
__icon__ = "🔍"
__examples__ = [example]
__author__ = "streamlit-extras"
__streamlit_min_version__ = "1.46.0"
