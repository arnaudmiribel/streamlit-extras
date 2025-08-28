from __future__ import annotations

from datetime import timedelta

import pandas as pd
import snowflake.snowpark as sp
import streamlit as st

from .. import extra


def _get_session() -> sp.Session:
    """
    Get or create a Snowpark session from the Streamlit connection.

    Returns:
        sp.Session: The Snowpark session object
    """
    if "snowpark_session" not in st.session_state:
        connection = st.connection("snowflake")
        st.session_state["snowpark_session"] = connection.session()
    return st.session_state["snowpark_session"]


@extra
def run_sql(
    query: str,
    ttl: timedelta | int | None = timedelta(hours=2),
    lowercase_columns: bool = True,
) -> pd.DataFrame:
    """
    Execute a SQL query and cache the results.

    Args:
        query (str): The SQL query to execute
        ttl (timedelta | int | None): Time-to-live for the cache. Defaults to 2 hours.
            Set to None to use the default cache invalidation.
        lowercase_columns (bool): Whether to convert column names to lowercase. Defaults to True.

    Returns:
        pd.DataFrame: The query results as a pandas DataFrame
    """

    @st.cache_data(ttl=ttl)
    def _run_sql(query: str) -> pd.DataFrame:
        return _get_session().sql(query).to_pandas()

    df = _run_sql(query)

    if lowercase_columns:
        df.columns = df.columns.str.lower()

    return df


@extra
def run_snowpark(
    df: sp.DataFrame,
    ttl: timedelta | int | None = timedelta(hours=2),
    lowercase_columns: bool = True,
) -> pd.DataFrame:
    """
    Convert a Snowpark DataFrame to a pandas DataFrame and cache the result.

    Args:
        df (sp.DataFrame): The Snowpark DataFrame to convert
        ttl (timedelta | int | None): Time-to-live for the cache. Defaults to 2 hours.
            Set to None to use the default cache invalidation.
        lowercase_columns (bool): Whether to convert column names to lowercase. Defaults to True.

    Returns:
        pd.DataFrame: The converted pandas DataFrame with cached results
    """

    @st.cache_data(ttl=ttl)
    def _run_snowpark(
        _df: sp.DataFrame, query: str, lowercase_columns: bool
    ) -> pd.DataFrame:
        _ = query
        df = _df.to_pandas()

        if lowercase_columns:
            df.columns = df.columns.str.lower()

        return df

    query = df._plan.queries[0].sql

    return _run_snowpark(df, query, lowercase_columns=lowercase_columns)


@extra
@st.cache_resource
def get_table(table_name: str) -> sp.Table:
    """
    Get a Snowpark table for use in building a query.

    Args:
        table_name (str): Name of the table to retrieve

    Returns:
        sp.Table: A cached Snowpark Table object that can be used for querying.
            The result is cached so that metadata is not re-fetched from the database.
    """
    return _get_session().table(table_name)
