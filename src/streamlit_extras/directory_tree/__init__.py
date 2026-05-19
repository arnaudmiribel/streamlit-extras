"""Directory tree visualization for Streamlit.

A collapsible directory tree component with Material icons, optional border,
and optional click-to-select functionality. Toggling directories is purely
client-side (no reruns). Selection can optionally trigger a rerun.
"""

from collections.abc import Callable
from datetime import date
from functools import cache
from typing import Any, Literal

import streamlit as st
import streamlit.components.v2
import streamlit.errors

from streamlit_extras import extra


def _on_select_change() -> None:
    """Callback function for when a node is selected."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.directory_tree",
        js="index-*.js",
        html='<div class="react-root"></div>',
        isolate_styles=False,
    )


@extra
def directory_tree(
    tree: dict[str, Any],
    *,
    expanded: bool | int = False,
    border: bool = False,
    color: str | None = "primary",
    on_select: Literal["rerun", "ignore"] = "ignore",
    height: int | None = None,
    key: str | None = None,
) -> str | None:
    """Display a collapsible directory tree.

    Renders a nested directory structure with Material icons and expand/collapse
    toggles. Toggling directories is purely client-side (no reruns). Optionally,
    clicking a node can return its path to Python.

    Args:
        tree: Nested dict representing the file tree. Keys are file/directory
            names. Values of None indicate files; dict values indicate
            directories containing more entries.
        expanded: Controls initial expansion. ``True`` expands all nodes,
            ``False`` collapses all. An integer expands nodes up to that
            depth (0 = all collapsed, 1 = top-level expanded, 2 = two
            levels deep, etc.).
        border: Whether to show a border around the tree container.
        color: Color for directory folder icons. Defaults to ``"primary"``
            which uses the Streamlit primary color. Pass any CSS color
            string (e.g. ``"#ff6600"``, ``"orange"``), or ``None`` to
            use the same text color as files (no special coloring).
        on_select: Selection mode. "ignore" means clicks don't trigger reruns
            (purely visual). "rerun" means clicking a node sends the path
            back to Python and triggers a rerun.
        height: Optional max height in pixels. If set, the tree scrolls
            when content exceeds this height.
        key: Unique key for this widget instance.

    Returns:
        The selected node path (e.g. "src/utils/helpers.py") when
        on_select="rerun" and a node has been clicked, otherwise None.

    Raises:
        StreamlitAPIException: If tree is not a dict.

    Example:

        ```python
        directory_tree(
            {
                "src": {"main.py": None, "utils": {"helpers.py": None}},
                "README.md": None,
            }
        )
        ```
    """
    if not isinstance(tree, dict):
        raise streamlit.errors.StreamlitAPIException(f"tree must be a dict, got {type(tree).__name__}")

    # Normalize expanded to a depth integer for the frontend:
    # True -> very large number (all expanded), False -> 0, int -> as-is
    if expanded is True:
        expand_depth = 999
    elif expanded is False:
        expand_depth = 0
    else:
        expand_depth = int(expanded)

    component = _get_component()

    data = {
        "tree": tree,
        "expand_depth": expand_depth,
        "border": border,
        "color": color,
        "selectable": on_select == "rerun",
        "height": height,
    }

    if on_select == "rerun":
        result = component(
            key=key,
            data=data,
            default={"selected": ""},
            on_selected_change=_on_select_change,
        )
        selected: str = result.get("selected", "")
        return selected or None

    component(key=key, data=data)
    return None


def example_basic() -> None:
    """Basic directory tree display."""
    st.write("### Basic Tree (collapsed by default)")
    directory_tree(
        {
            "src": {
                "app.py": None,
                "components": {
                    "header.tsx": None,
                    "sidebar.tsx": None,
                },
                "utils": {
                    "helpers.py": None,
                    "constants.py": None,
                },
            },
            "tests": {
                "test_app.py": None,
            },
            "README.md": None,
            "pyproject.toml": None,
        },
        key="basic_tree",
    )

    st.write("### Fully expanded")
    directory_tree(
        {
            "src": {
                "app.py": None,
                "components": {
                    "header.tsx": None,
                    "sidebar.tsx": None,
                },
                "utils": {
                    "helpers.py": None,
                    "constants.py": None,
                },
            },
            "tests": {
                "test_app.py": None,
            },
            "README.md": None,
            "pyproject.toml": None,
        },
        expanded=True,
        key="expanded_tree",
    )

    st.write("### Expand one level deep (expanded=1)")
    directory_tree(
        {
            "my_app": {
                "src": {
                    "main.py": None,
                    "models": {
                        "user.py": None,
                        "post.py": None,
                    },
                    "routes": {
                        "auth.py": None,
                        "api.py": None,
                    },
                },
                "tests": {
                    "test_main.py": None,
                    "test_models.py": None,
                },
                "pyproject.toml": None,
            },
        },
        expanded=1,
        key="depth1_tree",
    )


def example_colors() -> None:
    """Folder icon color options."""
    st.write("### Default (primary color)")
    directory_tree(
        {
            "project": {
                "src": {"index.ts": None, "utils": {"format.ts": None}},
                "package.json": None,
            },
        },
        expanded=True,
        border=True,
        key="color_primary",
    )

    st.write("### No color (color=None)")
    directory_tree(
        {
            "project": {
                "src": {"index.ts": None, "utils": {"format.ts": None}},
                "package.json": None,
            },
        },
        expanded=True,
        border=True,
        color=None,
        key="color_none",
    )

    st.write("### Custom colors")
    col1, col2, col3 = st.columns(3)
    with col1:
        directory_tree(
            {"docs": {"guide.md": None, "api.md": None}},
            expanded=True,
            color="#2196F3",
            key="color_blue",
        )
    with col2:
        directory_tree(
            {"src": {"main.py": None, "utils.py": None}},
            expanded=True,
            color="#4CAF50",
            key="color_green",
        )
    with col3:
        directory_tree(
            {"assets": {"logo.svg": None, "style.css": None}},
            expanded=True,
            color="#FF9800",
            key="color_orange",
        )


def example_height() -> None:
    """Fixed height with scrollable overflow."""
    st.write("### Fixed height (height=150)")
    directory_tree(
        {
            "large_project": {
                "src": {
                    "components": {
                        "Button.tsx": None,
                        "Modal.tsx": None,
                        "Sidebar.tsx": None,
                        "Header.tsx": None,
                        "Footer.tsx": None,
                        "Card.tsx": None,
                        "Avatar.tsx": None,
                    },
                    "hooks": {
                        "useAuth.ts": None,
                        "useTheme.ts": None,
                        "useData.ts": None,
                    },
                    "pages": {
                        "Home.tsx": None,
                        "Dashboard.tsx": None,
                        "Settings.tsx": None,
                        "Profile.tsx": None,
                    },
                    "App.tsx": None,
                    "index.tsx": None,
                },
                "public": {
                    "index.html": None,
                    "favicon.ico": None,
                },
                "package.json": None,
                "tsconfig.json": None,
                "README.md": None,
            },
        },
        expanded=True,
        border=True,
        height=150,
        key="height_tree",
    )

    st.write("### Long filenames get ellipsis")
    directory_tree(
        {
            "src": {
                "this_is_a_very_long_filename_that_should_be_truncated_with_ellipsis.tsx": None,
                "another_extremely_long_component_name_for_testing_overflow.test.tsx": None,
                "components": {
                    "SuperLongComponentNameThatExceedsTheContainerWidth.tsx": None,
                    "short.ts": None,
                },
            },
        },
        expanded=True,
        border=True,
        key="long_names_tree",
    )

    st.write("### Taller height (height=300)")
    directory_tree(
        {
            "monorepo": {
                "apps": {
                    "web": {
                        "src": {"App.tsx": None, "main.tsx": None},
                        "package.json": None,
                    },
                    "mobile": {
                        "src": {"App.tsx": None, "main.tsx": None},
                        "package.json": None,
                    },
                    "api": {
                        "src": {"server.ts": None, "routes.ts": None},
                        "package.json": None,
                    },
                },
                "packages": {
                    "ui": {"src": {"Button.tsx": None, "Input.tsx": None}},
                    "utils": {"src": {"format.ts": None, "validate.ts": None}},
                    "config": {"src": {"theme.ts": None, "env.ts": None}},
                },
                "turbo.json": None,
                "package.json": None,
            },
        },
        expanded=2,
        border=True,
        height=300,
        key="height_tree_tall",
    )


def example_interactive() -> None:
    """Interactive tree with click-to-select."""
    st.write("### Click to select a file")
    selected = directory_tree(
        {
            "frontend": {
                "src": {
                    "App.tsx": None,
                    "index.tsx": None,
                    "components": {
                        "Button.tsx": None,
                        "Modal.tsx": None,
                        "Sidebar.tsx": None,
                        "Header.tsx": None,
                    },
                },
                "package.json": None,
                "tsconfig.json": None,
            },
            "backend": {
                "main.py": None,
                "routes": {
                    "auth.py": None,
                    "api.py": None,
                    "users.py": None,
                },
                "models": {
                    "user.py": None,
                    "session.py": None,
                },
            },
        },
        on_select="rerun",
        border=True,
        expanded=2,
        height=200,
        key="interactive_tree",
    )
    if selected:
        st.success(f"Selected: `{selected}`")


__title__ = "Directory Tree"
__desc__ = "Collapsible directory tree with Material icons and optional click-to-select."
__icon__ = "🌲"
__examples__ = [example_basic, example_colors, example_height, example_interactive]
__author__ = "streamlit-extras"
__created_at__ = date(2026, 5, 15)
