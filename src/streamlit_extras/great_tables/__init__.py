from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Literal

import streamlit as st
import streamlit.components.v2

from .. import extra

if TYPE_CHECKING:
    from great_tables import GT

# CSS overrides that map Great Tables' hardcoded colors to Streamlit theme variables.
# These use high-specificity selectors to override GT's ID-scoped styles.
_THEME_CSS = """
:host {
    overflow-x: auto;
    overflow-y: auto;
}

/* Container wrapper - remove GT's default padding, let Streamlit handle it */
#gt-container > div {
    padding: 0 !important;
}

/* Base table styles */
#gt-container table {
    font-family: var(--st-font) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Main table - background and text colors */
#gt-container .gt_table {
    color: var(--st-text-color) !important;
    background-color: var(--st-background-color) !important;
    border-top-color: var(--st-border-color) !important;
    border-bottom-color: var(--st-border-color) !important;
}

/* Title and subtitle */
#gt-container .gt_title,
#gt-container .gt_subtitle {
    color: var(--st-text-color) !important;
}

/* Heading area */
#gt-container .gt_heading {
    background-color: var(--st-background-color) !important;
}

/* Column headings */
#gt-container .gt_col_headings {
    border-top-color: var(--st-border-color) !important;
    border-bottom-color: var(--st-border-color) !important;
}

#gt-container .gt_col_heading,
#gt-container .gt_column_spanner_outer {
    color: var(--st-text-color) !important;
    background-color: var(--st-secondary-background-color) !important;
}

/* Table body */
#gt-container .gt_table_body {
    border-top-color: var(--st-border-color) !important;
    border-bottom-color: var(--st-border-color) !important;
}

/* Data rows */
#gt-container .gt_row {
    color: var(--st-text-color) !important;
    border-top-color: var(--st-border-color-light, var(--st-border-color)) !important;
}

/* Striped rows - use a subtle variation of the secondary background */
#gt-container .gt_striped {
    color: var(--st-text-color) !important;
    background-color: var(--st-secondary-background-color) !important;
}

/* Stub (row labels) */
#gt-container .gt_stub,
#gt-container .gt_stub_row_group {
    color: var(--st-text-color) !important;
    background-color: var(--st-background-color) !important;
    border-right-color: var(--st-border-color) !important;
}

/* Group headings */
#gt-container .gt_group_heading,
#gt-container .gt_empty_group_heading {
    color: var(--st-text-color) !important;
    background-color: var(--st-secondary-background-color) !important;
    border-top-color: var(--st-border-color) !important;
    border-bottom-color: var(--st-border-color) !important;
}

/* Grand summary rows */
#gt-container .gt_grand_summary_row {
    color: var(--st-text-color) !important;
    background-color: var(--st-background-color) !important;
}

#gt-container .gt_first_grand_summary_row_bottom {
    border-top-color: var(--st-border-color) !important;
}

#gt-container .gt_last_grand_summary_row_top {
    border-bottom-color: var(--st-border-color) !important;
}

/* Source notes / footnotes */
#gt-container .gt_sourcenotes,
#gt-container .gt_sourcenote {
    color: var(--st-text-color) !important;
    background-color: var(--st-background-color) !important;
}

/* Column spanner borders */
#gt-container .gt_column_spanner {
    border-bottom-color: var(--st-border-color) !important;
}
"""

_COMPONENT_JS = """
export default function(component) {
    const { data, parentElement } = component;
    const container = parentElement.querySelector("#gt-container");
    if (!container) return () => {};

    const html = data?.html ?? "";
    const width = data?.width ?? "stretch";

    // Insert the Great Tables HTML
    container.innerHTML = html;

    // Handle width
    if (width === "stretch") {
        container.style.width = "100%";
        // Find the inner wrapper div and table, make them stretch
        const innerDiv = container.querySelector(":scope > div");
        if (innerDiv) {
            innerDiv.style.width = "100%";
        }
        const table = container.querySelector(".gt_table");
        if (table) {
            table.style.width = "100%";
        }
    } else if (typeof width === "number") {
        container.style.width = width + "px";
    }
    // "content" - no explicit width, use natural size

    return () => {};
}
"""

_GREAT_TABLES_COMPONENT = streamlit.components.v2.component(
    name="streamlit_extras.great_tables",
    html='<div id="gt-container"></div>',
    css=_THEME_CSS,
    js=_COMPONENT_JS,
)


@extra
def great_tables(
    table: GT,
    width: int | Literal["stretch", "content"] = "stretch",
    *,
    theme: Literal["streamlit"] | None = "streamlit",
) -> None:
    """
    Render a Great Tables object in Streamlit.

    Args:
        table: A Great Tables object.
        width: The width of the table. One of:
            - `"stretch"` (default): Stretch the table to the width of the container.
            - `"content"`: Use the table's natural width based on content.
            - `int`: A fixed width in pixels.
        theme: The theme to apply to the table. One of:
            - `"streamlit"` (default): Apply Streamlit's theme colors (text, background,
              borders) to the table. The table automatically adapts when the user
              switches between light and dark themes.
            - `None`: Preserve Great Tables' original styling.
    """
    # Apply width settings via tab_options for proper table sizing
    if width == "stretch":
        table = table.tab_options(container_width="100%", table_width="100%")
    elif isinstance(width, int):
        table = table.tab_options(container_width=f"{width}px", table_width=f"{width}px")
    # "content" - don't modify, use GT's default sizing

    html = table.as_raw_html()

    if theme == "streamlit":
        # Use CCv2 component with live theme support
        component_width: Literal["stretch", "content"] = "stretch" if width == "stretch" else "content"
        _GREAT_TABLES_COMPONENT(
            data={"html": html, "width": width},
            width=component_width,
        )
    else:
        # Fall back to st.html for users who want original GT styling
        st.html(html)


def example() -> None:
    """Basic example with S&P 500 data."""
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
        st.warning("This example requires the `great_tables` package. Install it with `pip install great-tables`.")


def example_column_spanners() -> None:
    """Example with column spanners and HTML labels."""
    try:
        from great_tables import GT, html
        from great_tables.data import airquality

        # Use first 10 rows of air quality data
        airquality_mini = airquality.head(10).assign(Year=1973)

        table = (
            GT(airquality_mini)
            .tab_header(
                title="New York Air Quality Measurements",
                subtitle="Daily measurements in New York City (May 1-10, 1973)",
            )
            .tab_spanner(label="Time", columns=["Year", "Month", "Day"])
            .tab_spanner(label="Measurement", columns=["Ozone", "Solar_R", "Wind", "Temp"])
            .cols_move_to_start(columns=["Year", "Month", "Day"])
            .cols_label(
                Ozone=html("Ozone,<br>ppbV"),
                Solar_R=html("Solar R.,<br>cal/m<sup>2</sup>"),
                Wind=html("Wind,<br>mph"),
                Temp=html("Temp,<br>&deg;F"),
            )
        )

        great_tables(table, width="stretch")
    except ImportError:
        st.warning("This example requires the `great_tables` package. Install it with `pip install great-tables`.")


def example_data_coloring() -> None:
    """Example with data coloring (heat map style)."""
    try:
        from great_tables import GT, html
        from great_tables.data import sza

        # Filter and pivot the solar zenith angle data
        # Filter to latitude 20 and morning hours, then pivot to wide format
        sza_filtered = sza[(sza["latitude"] == "20") & (sza["tst"] <= "1200")].dropna()

        # Pivot the data: months as rows, times as columns
        sza_pivot = sza_filtered.pivot(index="month", columns="tst", values="sza")
        sza_pivot = sza_pivot.reset_index()

        table = (
            GT(sza_pivot, rowname_col="month")
            .data_color(
                domain=[90, 0],
                palette=["rebeccapurple", "white", "orange"],
                na_color="white",
            )
            .tab_header(
                title="Solar Zenith Angles from 05:30 to 12:00",
                subtitle=html("Average monthly values at latitude of 20&deg;N."),
            )
            .sub_missing(missing_text="")
        )

        great_tables(table, width="stretch")
    except ImportError:
        st.warning("This example requires the `great_tables` package. Install it with `pip install great-tables`.")


def example_row_groups() -> None:
    """Example with row grouping by region."""
    try:
        from great_tables import GT
        from great_tables.data import countrypops

        # Define Oceania regions and their countries
        oceania = {
            "Australasia": ["AU", "NZ"],
            "Melanesia": ["NC", "PG", "SB", "VU"],
            "Micronesia": ["FM", "GU", "KI", "MH", "MP", "NR", "PW"],
            "Polynesia": ["PF", "WS", "TO", "TV"],
        }

        # Create mapping from country code to region
        country_to_region = {country: region for region, countries in oceania.items() for country in countries}

        # Filter to Oceania countries and years 2000, 2010, 2020
        oceania_codes = list(country_to_region.keys())
        years = [2000, 2010, 2020]

        filtered = countrypops[
            (countrypops["country_code_2"].isin(oceania_codes)) & (countrypops["year"].isin(years))
        ].copy()

        # Add region column
        filtered["region"] = filtered["country_code_2"].map(country_to_region)

        # Pivot to wide format (years as columns)
        wide_pops = filtered.pivot(index=["country_name", "region"], columns="year", values="population").reset_index()

        # Rename columns to strings for GT
        wide_pops.columns = [str(c) for c in wide_pops.columns]

        # Sort by 2020 population descending
        wide_pops = wide_pops.sort_values("2020", ascending=False)

        table = (
            GT(wide_pops)
            .tab_header(title="Populations of Oceania's Countries", subtitle="Years 2000, 2010, and 2020")
            .tab_stub(rowname_col="country_name", groupname_col="region")
            .cols_hide(columns="region")
            .fmt_integer(columns=["2000", "2010", "2020"])
        )

        great_tables(table, width="stretch")
    except ImportError:
        st.warning("This example requires the `great_tables` package. Install it with `pip install great-tables`.")


__title__ = "Great Tables"
__desc__ = """Render [Great Tables](https://posit-dev.github.io/great-tables/articles/intro.html) objects in Streamlit.
Great Tables allows you to create wonderful-looking display tables in Python.

The table automatically adapts to Streamlit's theme (light/dark) and updates live when the user switches themes.
"""
__icon__ = "🧮"
__examples__ = [example, example_column_spanners, example_data_coloring, example_row_groups]
__author__ = "Lukas Masuch"
__created_at__ = date(2025, 3, 10)
__playground__ = False
