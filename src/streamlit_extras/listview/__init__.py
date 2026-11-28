from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

import streamlit as st

from .. import extra

if TYPE_CHECKING:
    from collections.abc import Iterable

    from streamlit_listview import listview as listview
else:

    @extra
    def listview(
        label: str, options: Iterable[Any] | None = None, **widget_options: Any
    ) -> dict[str, Any] | str | int | list[Any] | None:
        """Render a selectable list using streamlit-listview.

        Returns:
            The selected option or None in single mode, or a list of options in multi mode.
        """
        # ListView 1.1 registers its component on import and needs a running app.
        from streamlit_listview import listview as render

        return render(label, options, **widget_options)


def example() -> None:
    framework = listview(
        "Select a Python framework",
        ["Streamlit", "Gradio", "Dash", "Flask", "Shiny"],
        selection_mode="single",
        enable_search=True,
        accept_new_options=True,
    )
    st.write("Selected framework:", framework)


def example_grouped_workshops() -> None:
    workshops = [
        {"id": "charts", "label": "Build a dashboard", "group": "Visualization"},
        {"id": "maps", "label": "Map your data (full)", "group": "Visualization", "disabled": True},
        {"id": "colors", "label": "Choose accessible colors", "group": "Visualization"},
        {"id": "forms", "label": "Design a form", "group": "App development"},
        {"id": "tests", "label": "Test your app", "group": "App development"},
        {"id": "clean", "label": "Clean a dataset", "group": "Data preparation"},
        {"id": "clinic", "label": "Bring a project to the help desk"},
    ]
    with st.expander("Group settings", expanded=True):
        collapsible = st.toggle("Allow groups to collapse", value=True)
        order = st.selectbox("Group order", ["As listed", "A to Z", "Z to A"])

    selected = listview(
        "Choose up to two workshops",
        workshops,
        selection_mode="multi",
        default=["charts"],
        collapsible_groups=collapsible,
        sort=None if order == "As listed" else "groups",
        sort_ascending=order != "Z to A",
        ungrouped_label="General",
        max_selections=2,
        key="workshop_schedule",
    )
    st.write("Selected workshop records:", selected)


def example_formatted_ticket_ids() -> None:
    tickets = {104: "Fix the login redirect", 218: "Restore CSV export", 309: "Update the setup guide"}
    ticket_id = listview(
        "Find a support ticket",
        list(tickets),
        format_func=lambda number: f"#{number}: {tickets[number]}",
        enable_search=True,
        search_placeholder="Search by ticket number or title",
        key="support_ticket",
    )
    if ticket_id is not None:
        st.write("Selected ticket ID:", ticket_id)


def example_appearance() -> None:
    with st.expander("Appearance settings", expanded=True):
        layout, rows = st.columns(2)
        height = layout.slider("List height (px)", 120, 360, 200, step=20)
        full_width = layout.toggle("Use full width", value=True)
        item_height = rows.slider("Minimum row height (px)", 24, 64, 40, step=4)
        font_size = rows.slider("Row font size (px)", 12, 24, 16)
        grid_lines = rows.toggle("Show row dividers", value=True)

    section = listview(
        "Report outline",
        ["Overview", "Revenue", "Expenses", "Forecast", "Risks", "Appendix"],
        default="Overview",
        height=height,
        width="stretch" if full_width else 280,
        item_height=item_height,
        content_font_size=font_size,
        show_grid_lines=grid_lines,
        key="report_outline",
    )
    st.write("Selected section:", section)


def _test_gallery_example() -> None:
    from unittest.mock import patch

    with patch(f"{__name__}.listview", return_value="Django") as widget, patch.object(st, "write") as write:
        example()

    widget.assert_called_once()
    assert "Django" not in widget.call_args.args[1]
    assert widget.call_args.kwargs["selection_mode"] == "single"
    assert widget.call_args.kwargs["enable_search"] and widget.call_args.kwargs["accept_new_options"]
    write.assert_called_once_with("Selected framework:", "Django")


def _test_forwards_multi_selection() -> None:
    import sys
    from unittest.mock import Mock, patch

    options = [{"id": "flask"}, {"id": "dash"}]
    selected = [options[1], options[0]]
    upstream = Mock()
    upstream.listview.return_value = selected
    with patch.dict(sys.modules, streamlit_listview=upstream):
        result = listview("Frameworks", options, selection_mode="multi", key="frameworks")

    upstream.listview.assert_called_once_with("Frameworks", options, selection_mode="multi", key="frameworks")
    assert result is selected


__title__ = "List View"
__icon__ = "📋"
__author__ = "Leland Grunt"
__created_at__ = date(2026, 11, 25)
__examples__ = [example, example_grouped_workshops, example_formatted_ticket_ids, example_appearance]
__pypi_name__ = "streamlit-listview"
__package_name__ = "streamlit_listview"
__github_repo__ = "LelandGrunt/streamlit-listview"
__streamlit_cloud_url__ = "https://st-listview-demo.streamlit.app/"
__forum_url__ = "https://discuss.streamlit.io/t/new-component-streamlit-listview-a-native-feeling-list-with-search-groups-and-multi-select/122659"
__desc__ = (
    "Choose one or more items from a searchable list. "
    f"[Try the playground]({__streamlit_cloud_url__}) or [read the forum discussion]({__forum_url__})."
)
__playground__ = False  # The hosted demo is the playground, not the docs' stlite embed.
__streamlit_min_version__ = "1.54.0"
__tests__ = [_test_gallery_example, _test_forwards_multi_selection]
