"""Utility functions to handle repeated GUI tasks for the dashboard."""
import itertools
from datetime import date, timedelta
from io import StringIO

import pandas as pd
import streamlit as st
from pandas._libs.tslibs.timestamps import Timestamp

ST_COLOR_PALETTE = {
    "red": {
        "100": "#7d353b",
        "90": "#bd4043",
        "80": "#ff2b2b",
        "70": "#ff4b4b",
        "60": "#ff6c6c",
        "50": "#ff8c8c",
        "40": "#ffabab",
        "30": "#ffc7c7",
        "20": "#ffdede",
        "10": "#fff0f0",
    },
    "orange": {
        "100": "#d95a00",
        "90": "#ed6f13",
        "80": "#ff8700",
        "70": "#ffa421",
        "60": "#ffbd45",
        "50": "#ffd16a",
        "40": "#ffe08e",
        "30": "#ffecb0",
        "20": "#fff6d0",
        "10": "#fffae8",
    },
    "yellow": {
        "100": "#dea816",
        "90": "#edbb16",
        "80": "#faca2b",
        "70": "#ffe312",
        "60": "#fff835",
        "50": "#ffff59",
        "40": "#ffff7d",
        "30": "#ffffa0",
        "20": "#ffffc2",
        "10": "#ffffe1",
    },
    "green": {
        "100": "#177233",
        "90": "#158237",
        "80": "#09ab3b",
        "70": "#21c354",
        "60": "#3dd56d",
        "50": "#5ce488",
        "40": "#7defa1",
        "30": "#9ef6bb",
        "20": "#c0fcd3",
        "10": "#dffde9",
    },
    "blue-green": {
        "100": "#246e69",
        "90": "#2c867c",
        "80": "#29b09d",
        "70": "#00d4b1",
        "60": "#20e7c5",
        "50": "#45f4d5",
        "40": "#6bfde3",
        "30": "#93ffee",
        "20": "#bafff7",
        "10": "#dcfffb",
    },
    "light-blue": {
        "100": "#15799e",
        "90": "#0d8cb5",
        "80": "#00a4d4",
        "70": "#00c0f2",
        "60": "#24d4ff",
        "50": "#4be4ff",
        "40": "#73efff",
        "30": "#9af8ff",
        "20": "#bffdff",
        "10": "#e0feff",
    },
    "blue": {
        "100": "#004280",
        "90": "#0054a3",
        "80": "#0068c9",
        "70": "#1c83e1",
        "60": "#3d9df3",
        "50": "#60b4ff",
        "40": "#83c9ff",
        "30": "#a6dcff",
        "20": "#c7ebff",
        "10": "#e4f5ff",
    },
    "violet": {
        "100": "#3f3163",
        "90": "#583f84",
        "80": "#6d3fc0",
        "70": "#803df5",
        "60": "#9a5dff",
        "50": "#b27eff",
        "40": "#c89dff",
        "30": "#dbbbff",
        "20": "#ebd6ff",
        "10": "#f5ebff",
    },
    "gray": {
        "100": "#0e1117",
        "90": "#262730",
        "80": "#555867",
        "70": "#808495",
        "60": "#a3a8b8",
        "50": "#bfc5d3",
        "40": "#d5dae5",
        "30": "#e6eaf1",
        "20": "#f0f2f6",
        "10": "#fafafa",
    },
}


def color(name):
    """Returns a color from the streamlit color palette, e.g. red-100, as hex."""
    hue, intensity = name.rsplit("-", 1)
    return ST_COLOR_PALETTE[hue][intensity]


ST_COLOR_PALETTE = {
    "red": {
        "100": "#7d353b",
        "90": "#bd4043",
        "80": "#ff2b2b",
        "70": "#ff4b4b",
        "60": "#ff6c6c",
        "50": "#ff8c8c",
        "40": "#ffabab",
        "30": "#ffc7c7",
        "20": "#ffdede",
        "10": "#fff0f0",
    },
    "orange": {
        "100": "#d95a00",
        "90": "#ed6f13",
        "80": "#ff8700",
        "70": "#ffa421",
        "60": "#ffbd45",
        "50": "#ffd16a",
        "40": "#ffe08e",
        "30": "#ffecb0",
        "20": "#fff6d0",
        "10": "#fffae8",
    },
    "yellow": {
        "100": "#dea816",
        "90": "#edbb16",
        "80": "#faca2b",
        "70": "#ffe312",
        "60": "#fff835",
        "50": "#ffff59",
        "40": "#ffff7d",
        "30": "#ffffa0",
        "20": "#ffffc2",
        "10": "#ffffe1",
    },
    "green": {
        "100": "#177233",
        "90": "#158237",
        "80": "#09ab3b",
        "70": "#21c354",
        "60": "#3dd56d",
        "50": "#5ce488",
        "40": "#7defa1",
        "30": "#9ef6bb",
        "20": "#c0fcd3",
        "10": "#dffde9",
    },
    "blue-green": {
        "100": "#246e69",
        "90": "#2c867c",
        "80": "#29b09d",
        "70": "#00d4b1",
        "60": "#20e7c5",
        "50": "#45f4d5",
        "40": "#6bfde3",
        "30": "#93ffee",
        "20": "#bafff7",
        "10": "#dcfffb",
    },
    "light-blue": {
        "100": "#15799e",
        "90": "#0d8cb5",
        "80": "#00a4d4",
        "70": "#00c0f2",
        "60": "#24d4ff",
        "50": "#4be4ff",
        "40": "#73efff",
        "30": "#9af8ff",
        "20": "#bffdff",
        "10": "#e0feff",
    },
    "blue": {
        "100": "#004280",
        "90": "#0054a3",
        "80": "#0068c9",
        "70": "#1c83e1",
        "60": "#3d9df3",
        "50": "#60b4ff",
        "40": "#83c9ff",
        "30": "#a6dcff",
        "20": "#c7ebff",
        "10": "#e4f5ff",
    },
    "violet": {
        "100": "#3f3163",
        "90": "#583f84",
        "80": "#6d3fc0",
        "70": "#803df5",
        "60": "#9a5dff",
        "50": "#b27eff",
        "40": "#c89dff",
        "30": "#dbbbff",
        "20": "#ebd6ff",
        "10": "#f5ebff",
    },
    "gray": {
        "100": "#0e1117",
        "90": "#262730",
        "80": "#555867",
        "70": "#808495",
        "60": "#a3a8b8",
        "50": "#bfc5d3",
        "40": "#d5dae5",
        "30": "#e6eaf1",
        "20": "#f0f2f6",
        "10": "#fafafa",
    },
}


HEADER_COLOR_CYCLE = itertools.cycle(
    [
        "light-blue-70",
        "orange-70",
        "blue-green-70",
        "blue-70",
        "violet-70",
        "red-70",
        "green-70",
        "yellow-80",
    ]
)


def colored_header(label: str, description: str = None, color_name: str = None):
    """
    Shows a header with a colored underline and an optional description.
    """
    if color_name is None:
        color_name = next(HEADER_COLOR_CYCLE)
    st.subheader(label)
    st.write(
        f'<hr style="background-color: {color(color_name)}; margin-top: 0; margin-bottom: 0; height: 3px; border: none; border-radius: 3px;">',
        unsafe_allow_html=True,
    )
    if description:
        st.caption(description)


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


def convert_timestamps_to_string(df: pd.DataFrame) -> pd.DataFrame:
    for col in df:
        if df[col].dtype.type == Timestamp:
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def pretty_print_df(
    name: str,
    df: pd.DataFrame,
    allow_html: bool = False,
    **format_kwargs,
):
    """
    Prints out a dataframe, handling NANs properly and including useful metadata such as
    column types and number of rows.

    This function solves some dataframe display bugs

    Parameters
    ----
    name: str
        Pretty print a name for this dataframe
    df: pd.DataFrame
        The dataframe to proint
    """
    DEFAULT_N_ROWS = 500
    st.subheader(name)

    if "na_rep" not in format_kwargs:
        format_kwargs["na_rep"] = "n/a"

    # Turn nonpositive numbers red.
    def _cell_colorer(x):
        try:
            if x is True:
                return "color: green"
            if x <= 0:
                return "color: red"
        except TypeError:
            pass
        return ""

    # This is where we'll display the data frame
    dataframe_location = st.empty()
    st.caption(f"`{len(df)}` elements in {name}")  # type: ignore

    # Display options
    with st.expander(f"Show options for {name}"):
        # Let the user select the number of rows.
        n_rows = st.slider(f"Rows for {name}", 0, len(df), min(DEFAULT_N_ROWS, len(df)))

        # Provide a link to download a CSV file.
        if st.checkbox(f"Show download link for {name}"):
            csv = df[:n_rows].to_csv(index=True)
            filename = name.replace(" ", "_").lower() + ".csv"
            st.download_button(f"Download {n_rows} rows", data=csv, file_name=filename)

        # Show more details about the dataframe
        if st.checkbox(f"Show info for {name}"):
            str_buffer = StringIO()
            df.info(buf=str_buffer)
            st.code(str_buffer.getvalue())

    # Apply these stylings.
    try:
        df = df[:n_rows]
        styled = df.style.format(**format_kwargs).applymap(_cell_colorer)
        if allow_html:
            dataframe_location.write(styled.to_html(), unsafe_allow_html=True)
        else:
            dataframe_location.dataframe(styled)
    except ValueError:
        styled = (
            df.reset_index()[:n_rows]
            .style.format(**format_kwargs)
            .applymap(_cell_colorer)
        )
        if allow_html:
            dataframe_location.write(styled.to_html(), unsafe_allow_html=True)
        else:
            dataframe_location.dataframe(styled)


def space(num_lines: int = 1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")


def week_paginator(key: str = "week_paginator"):
    """Shows a widget to paginate weeks, returns start & end date of selected week."""

    # Store page number in session state.
    if key not in st.session_state:
        st.session_state[key] = 0

    def next_page():
        st.session_state[key] += 1

    def prev_page():
        st.session_state[key] -= 1

    # Show buttons to increase or decrease the selected week/page.
    col1, col2, col3, _ = st.columns([0.09, 0.22, 0.09, 0.6])
    if st.session_state[key] < 0:
        col3.button(">", on_click=next_page)
    else:
        col3.write("")  # this makes the empty column show up on mobile
    if st.session_state[key] > -52:
        col1.button("<", on_click=prev_page)
    else:
        col1.write("")  # this makes the empty column show up on mobile

    # Calculate start and end date of the selected week based on page number.
    end_date = date.today() + timedelta(
        7 * st.session_state[key]
    )  # ...page is negative!
    start_date = end_date - timedelta(6)

    # Show selected week between the buttons.
    col2.write(start_date.strftime("%d %b") + " to " + end_date.strftime("%d %b"))

    return start_date, end_date
