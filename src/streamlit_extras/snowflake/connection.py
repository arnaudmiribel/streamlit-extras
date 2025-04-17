from __future__ import annotations

from datetime import timedelta

import pandas as pd
import snowflake.snowpark as sp
import streamlit as st


def _get_session() -> sp.Session:
    if "snowpark_session" not in st.session_state:
        connection = st.connection("snowflake")
        st.session_state["snowpark_session"] = connection.session()
    return st.session_state["snowpark_session"]


def run_sql(
    query: str,
    ttl: timedelta | int | None = timedelta(hours=2),
    lowercase_columns: bool = True,
):
    """
    Execute a SQL query and cache the results.

    Args:
        query: The SQL query to execute
        ttl: Time-to-live for the cache. Defaults to 2 hours.
            Set to None to use the default cache invalidation.

    Returns:
        pandas.DataFrame: The query results as a pandas DataFrame
    """

    @st.cache_data(ttl=ttl)
    def _run_sql(query: str) -> pd.DataFrame:
        return _get_session().sql(query).to_pandas()

    df = _run_sql(query)

    if lowercase_columns:
        df.columns = df.columns.str.lower()

    return df


def run_snowpark(
    df: sp.DataFrame,
    ttl: timedelta | int | None = timedelta(hours=2),
    lowercase_columns: bool = True,
) -> pd.DataFrame:
    """Converts a snowpark dataframe to a pandas dataframe and caches the result."""

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


@st.cache_resource
def get_table(table_name: str) -> sp.Table:
    return _get_session().table(table_name)
