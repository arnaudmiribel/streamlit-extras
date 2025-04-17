import streamlit as st

from .connection import get_table, run_snowpark, run_sql


def snowpark_example():
    df = get_table("my_table").select("a", "b", "c").limit(10)
    st.dataframe(run_snowpark(df))


def sql_example():
    df = run_sql("select a, b, c from my_table limit 10")
    st.dataframe(df)


__funcs__ = [get_table, run_snowpark, run_sql]
__all__ = ["get_table", "run_snowpark", "run_sql"]
__title__ = "Snowflake Utilities"
__desc__ = "Utilities for Streamlit-in-Snowflake"
__icon__ = "❄️"
__author__ = "Zachary Blackwood"
__examples__ = {
    snowpark_example: [get_table, run_snowpark],
    sql_example: [run_sql],
}
