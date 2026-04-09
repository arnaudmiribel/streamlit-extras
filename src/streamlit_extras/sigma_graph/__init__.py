"""Sigma Graph - Interactive network graph visualization using sigma.js.

A high-performance WebGL-based graph visualization component that accepts NetworkX
graphs or JSON-serializable node-link dictionaries.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import TYPE_CHECKING, Any, Literal, TypedDict

import streamlit as st
import streamlit.components.v2
import streamlit.errors
from typing_extensions import Required

from streamlit_extras import extra

if TYPE_CHECKING:
    from collections.abc import Callable

    import networkx as nx


class SigmaGraphData(TypedDict, total=False):
    """Node-link format for graph data.

    Attributes:
        nodes: List of node dicts, each with at least an "id" key.
        edges: List of edge dicts, each with "source" and "target" keys.
        directed: Whether the graph is directed. Default: False.
        multigraph: Whether the graph allows multiple edges between nodes. Default: False.
        graph: Graph-level attributes.
    """

    nodes: Required[list[dict[str, Any]]]
    edges: Required[list[dict[str, Any]]]
    directed: bool
    multigraph: bool
    graph: dict[str, Any]


class SigmaGraphSelection(TypedDict):
    """Selection data returned when a node or edge is clicked.

    Attributes:
        type: Whether a "node" or "edge" was selected.
        id: The ID of the selected node or edge key.
        attributes: All attributes of the selected element.
    """

    type: Literal["node", "edge"]
    id: str
    attributes: dict[str, Any]


def _on_select() -> None:
    """Default callback for selection events."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.sigma_graph",
        js="index-*.js",
        html='<div class="sigma-root"></div>',
    )


def _networkx_to_node_link(
    graph: nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph,
) -> SigmaGraphData:
    """Convert a NetworkX graph to node-link format.

    Args:
        graph: A NetworkX graph object.

    Returns:
        A dict in SigmaGraphData format.
    """
    import networkx as nx

    data = nx.node_link_data(graph)
    # NetworkX 3.x may use "links" or "edges" depending on version/settings
    edges = data.get("links", data.get("edges", []))
    return SigmaGraphData(
        nodes=data.get("nodes", []),
        edges=edges,
        directed=data.get("directed", False),
        multigraph=data.get("multigraph", False),
        graph=data.get("graph", {}),
    )


def _compute_layout(
    graph_data: SigmaGraphData,
    layout: Literal["spring", "circular", "kamada_kawai", "random"],
) -> SigmaGraphData:
    """Compute node positions using NetworkX layout algorithms.

    Args:
        graph_data: The graph data in node-link format.
        layout: The layout algorithm to use.

    Returns:
        The graph data with x and y attributes set on nodes.

    Raises:
        StreamlitAPIException: If NetworkX is not installed.
        ValueError: If an unknown layout algorithm is specified.
    """
    try:
        import networkx as nx
    except ImportError as e:
        raise streamlit.errors.StreamlitAPIException(
            f"NetworkX is required for the '{layout}' layout algorithm. Install it with: pip install networkx"
        ) from e

    # Reconstruct a NetworkX graph for layout computation
    # Provide both "links" and "edges" keys for compatibility across NetworkX versions
    # (NX 2.x uses "links", NX 3.x uses "edges" by default)
    edges = graph_data["edges"]
    nx_graph = nx.node_link_graph(
        {
            "nodes": graph_data["nodes"],
            "links": edges,  # For NetworkX 2.x
            "edges": edges,  # For NetworkX 3.x
            "directed": graph_data.get("directed", False),
            "multigraph": graph_data.get("multigraph", False),
            "graph": graph_data.get("graph", {}),
        },
    )

    # Compute layout
    if layout == "spring":
        pos = nx.spring_layout(nx_graph)
    elif layout == "circular":
        pos = nx.circular_layout(nx_graph)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(nx_graph)
    elif layout == "random":
        pos = nx.random_layout(nx_graph)
    else:
        raise ValueError(f"Unknown layout: {layout}")

    # Scale positions to a reasonable range for sigma.js
    # NetworkX layouts typically produce positions in [-1, 1] or [0, 1]
    # We scale to [-100, 100] for sigma
    scale = 100

    # Update node positions
    nodes_with_pos = []
    for node in graph_data["nodes"]:
        node_id = node["id"]
        if node_id in pos:
            x, y = pos[node_id]
            node_copy = dict(node)
            node_copy["x"] = float(x * scale)
            node_copy["y"] = float(y * scale)
            nodes_with_pos.append(node_copy)
        else:
            nodes_with_pos.append(node)

    return SigmaGraphData(
        nodes=nodes_with_pos,
        edges=graph_data["edges"],
        directed=graph_data.get("directed", False),
        multigraph=graph_data.get("multigraph", False),
        graph=graph_data.get("graph", {}),
    )


def _has_positions(graph_data: SigmaGraphData) -> bool:
    """Check if all nodes have x and y positions.

    Args:
        graph_data: The graph data to check.

    Returns:
        True if all nodes have x and y attributes.
    """
    return all("x" in node and "y" in node for node in graph_data["nodes"])


def _is_networkx_graph(data: Any) -> bool:
    """Check if data is a NetworkX graph type.

    Args:
        data: The data to check.

    Returns:
        True if data is a NetworkX graph.
    """
    try:
        import networkx as nx

        return isinstance(data, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph))
    except ImportError:
        return False


@extra
def sigma_graph(
    data: nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph | SigmaGraphData,
    *,
    layout: Literal["force", "spring", "circular", "kamada_kawai", "random"] | None = "force",
    width: int | Literal["stretch"] = "stretch",
    height: int = 500,
    node_color: str | None = None,
    edge_color: str | None = None,
    node_size: int | str = 8,
    selection_mode: Literal["nodes", "edges", "all"] = "nodes",
    on_select: Literal["ignore", "rerun"] | Callable[[SigmaGraphSelection], None] = "ignore",
    key: str | None = None,
) -> SigmaGraphSelection | None:
    """Display an interactive network graph using sigma.js.

    sigma.js is a high-performance WebGL-based graph visualization library that handles
    thousands of nodes smoothly with built-in pan, zoom, and hover interactions.

    Args:
        data: Graph data to visualize. Accepts NetworkX graphs (Graph, DiGraph,
            MultiGraph, MultiDiGraph) or a dict in node-link format with "nodes"
            and "edges" keys.
        layout: Layout algorithm for positioning nodes.
            - "force": ForceAtlas2 force-directed layout computed in the browser
              with animated settling. Best for interactive exploration.
            - "spring": NetworkX spring_layout (Fruchterman-Reingold).
            - "circular": Nodes arranged in a circle.
            - "kamada_kawai": Minimizes edge crossing.
            - "random": Random positions.
            - None: No layout computation. Positions must be provided via node
              x/y attributes.
        width: Width of the graph container. "stretch" fills the container width;
            an integer sets a fixed width in pixels.
        height: Height of the graph container in pixels.
        node_color: Default color for nodes (CSS color string). Overridden by
            per-node "color" attribute. If None, uses Streamlit theme primary color.
        edge_color: Default color for edges (CSS color string). Overridden by
            per-edge "color" attribute. If None, uses Streamlit theme muted color.
        node_size: How to size nodes.
            - int (default 8): Uniform size for all nodes.
            - "degree": Scale size by node degree (number of connections).
            - str: Name of a node attribute to use for sizing.
        selection_mode: What can be selected: "nodes" only, "edges" only, or "all"
            for both.
        on_select: Behavior when user clicks a selectable element.
            - "ignore": Disables selection (default).
            - "rerun": Triggers a rerun when an element is clicked.
            - Callable: Function called with the SigmaGraphSelection.
        key: Unique key for the widget. Required when on_select is "rerun" or
            a callable.

    Returns:
        When on_select="ignore": Always returns None.
        When on_select="rerun": Returns SigmaGraphSelection with the clicked element,
            or None if nothing is selected.
        When on_select is a callable: The callback receives the selection and
            returns None.

    Raises:
        StreamlitAPIException: If layout=None and nodes lack x/y positions, or if
            on_select requires a key but none is provided.

    Example:
        ```python
        import networkx as nx
        import streamlit as st
        from streamlit_extras.sigma_graph import sigma_graph

        G = nx.karate_club_graph()
        sigma_graph(G)
        ```
    """
    # Validate on_select requires key
    if on_select != "ignore" and key is None:
        raise streamlit.errors.StreamlitAPIException("A 'key' is required when 'on_select' is 'rerun' or a callable.")

    # Convert NetworkX graph to node-link format if needed
    if _is_networkx_graph(data):
        graph_data = _networkx_to_node_link(data)
    else:
        # Assume it's already a dict in SigmaGraphData format
        # Accept both "edges" and "links" keys (NetworkX uses "links" by default)
        edges = data.get("edges", data.get("links", []))
        graph_data = SigmaGraphData(
            nodes=data.get("nodes", []),
            edges=edges,
            directed=data.get("directed", False),
            multigraph=data.get("multigraph", False),
            graph=data.get("graph", {}),
        )

    # Handle layout computation
    use_force_layout = False
    if layout is None:
        # Ensure all nodes have positions
        if not _has_positions(graph_data):
            raise streamlit.errors.StreamlitAPIException(
                "When layout=None, all nodes must have 'x' and 'y' attributes."
            )
    elif layout == "force":
        # Force layout is computed in the browser
        use_force_layout = True
    else:
        # Compute layout in Python using NetworkX
        graph_data = _compute_layout(graph_data, layout)

    # Set up callback handling
    callback_fn = _on_select
    selection_enabled = on_select != "ignore"

    # Track the last processed selection to avoid repeated callback invocations
    last_selection_key = f"_sigma_graph_last_selection_{key}"

    if callable(on_select):

        def wrapped_callback() -> None:
            if key is None:
                return

            component_state = st.session_state.get(key, {})
            selection_state = component_state.get("selection")
            if selection_state is None:
                return

            # Create a hashable representation of the current selection
            current_sel_id = (selection_state.get("type"), selection_state.get("id"))
            last_sel_id = st.session_state.get(last_selection_key)

            # Only invoke callback if the selection actually changed
            if current_sel_id != last_sel_id:
                st.session_state[last_selection_key] = current_sel_id
                on_select(
                    SigmaGraphSelection(
                        type=selection_state.get("type", "node"),
                        id=selection_state.get("id", ""),
                        attributes=selection_state.get("attributes", {}),
                    )
                )

        callback_fn = wrapped_callback

    # Get current selection from session state to pass back to frontend for visual indication
    current_selection = None
    if key is not None and selection_enabled:
        component_state = st.session_state.get(key, {})
        selection_state = component_state.get("selection")
        if selection_state is not None:
            current_selection = {
                "type": selection_state.get("type"),
                "id": selection_state.get("id"),
            }

    component = _get_component()

    # Build node size config
    if isinstance(node_size, int):
        node_size_config: dict[str, Any] = {"mode": "uniform", "value": node_size}
    elif node_size == "degree":
        node_size_config = {"mode": "degree"}
    else:
        node_size_config = {"mode": "attribute", "attribute": node_size}

    result = component(
        key=key,
        data={
            "graph": {
                "nodes": graph_data["nodes"],
                "edges": graph_data["edges"],
                "directed": graph_data.get("directed", False),
                "multigraph": graph_data.get("multigraph", False),
            },
            "useForceLayout": use_force_layout,
            "width": width,
            "height": height,
            "nodeColor": node_color,
            "edgeColor": edge_color,
            "nodeSizeConfig": node_size_config,
            "selectionMode": selection_mode,
            "selectionEnabled": selection_enabled,
            "currentSelection": current_selection,
        },
        default={"selection": None},
        on_selection_change=callback_fn,
    )

    # Handle selection result
    selection_data = result.get("selection")

    if selection_data is not None and selection_enabled:
        selection = SigmaGraphSelection(
            type=selection_data.get("type", "node"),
            id=selection_data.get("id", ""),
            attributes=selection_data.get("attributes", {}),
        )

        # For callable on_select, the callback is invoked in wrapped_callback
        # via on_selection_change, so we just return None here
        if callable(on_select):
            return None

        return selection

    return None


def example_basic() -> None:
    """Basic example with a simple graph."""
    st.write("### Basic NetworkX Graph")
    st.write("Display a graph with the default force-directed layout.")

    # Create a simple graph without NetworkX for the example
    graph = {
        "nodes": [
            {"id": "Alice", "label": "Alice", "size": 15},
            {"id": "Bob", "label": "Bob", "size": 12},
            {"id": "Carol", "label": "Carol", "size": 10},
            {"id": "Dave", "label": "Dave", "size": 10},
        ],
        "edges": [
            {"source": "Alice", "target": "Bob"},
            {"source": "Alice", "target": "Carol"},
            {"source": "Bob", "target": "Carol"},
            {"source": "Carol", "target": "Dave"},
        ],
    }

    sigma_graph(graph, height=400)


def example_styled() -> None:
    """Example with custom colors and sizes."""
    st.write("### Styled Graph")
    st.write("Customize node colors and sizes based on data.")

    graph = {
        "directed": True,
        "nodes": [
            {"id": "streamlit", "label": "Streamlit", "size": 25, "color": "#ff4b4b"},
            {"id": "tornado", "label": "Tornado", "size": 12, "color": "#83c9ff"},
            {"id": "pandas", "label": "Pandas", "size": 18, "color": "#0068c9"},
            {"id": "numpy", "label": "NumPy", "size": 18, "color": "#0068c9"},
            {"id": "pillow", "label": "Pillow", "size": 10, "color": "#83c9ff"},
        ],
        "edges": [
            {"source": "streamlit", "target": "tornado", "size": 2},
            {"source": "streamlit", "target": "pandas", "size": 2},
            {"source": "streamlit", "target": "pillow", "size": 1},
            {"source": "pandas", "target": "numpy", "size": 3},
        ],
    }

    sigma_graph(graph, height=450, layout="circular")


def example_interactive() -> None:
    """Example with node selection."""
    st.write("### Interactive Selection")
    st.write("Click on a node to see its details.")

    graph = {
        "nodes": [
            {"id": "1", "label": "Node 1", "group": "A", "size": 12},
            {"id": "2", "label": "Node 2", "group": "A", "size": 15},
            {"id": "3", "label": "Node 3", "group": "B", "size": 10},
            {"id": "4", "label": "Node 4", "group": "B", "size": 18},
            {"id": "5", "label": "Node 5", "group": "C", "size": 14},
        ],
        "edges": [
            {"source": "1", "target": "2"},
            {"source": "2", "target": "3"},
            {"source": "3", "target": "4"},
            {"source": "4", "target": "5"},
            {"source": "5", "target": "1"},
            {"source": "2", "target": "4"},
        ],
    }

    selection = sigma_graph(graph, height=400, on_select="rerun", key="interactive_graph")

    if selection:
        st.success(f"Selected {selection['type']}: **{selection['id']}**")
        with st.expander("Attributes"):
            st.json(selection["attributes"])
    else:
        st.info("Click on a node to select it.")


def example_networkx() -> None:
    """Example with real NetworkX graphs."""
    import networkx as nx

    st.write("### NetworkX Graph Examples")
    st.write("Explore different graph datasets and generators from NetworkX.")

    # Graph options - mix of classic graphs and parameterized generators
    graph_options: dict[str, Callable[[], nx.Graph]] = {
        "Karate Club (34 nodes)": nx.karate_club_graph,
        "Les Misérables (77 nodes)": nx.les_miserables_graph,
        "Florentine Families (15 nodes)": nx.florentine_families_graph,
        "Barabási-Albert (500 nodes)": lambda: nx.barabasi_albert_graph(500, 3),
        "Barabási-Albert (1000 nodes)": lambda: nx.barabasi_albert_graph(1000, 2),
        "Watts-Strogatz (500 nodes)": lambda: nx.watts_strogatz_graph(500, 4, 0.3),
        "Random Geometric (400 nodes)": lambda: nx.random_geometric_graph(400, 0.1),
    }

    layout_options: dict[str, str] = {
        "Force (ForceAtlas2)": "force",
        "Spring (Fruchterman-Reingold)": "spring",
        "Circular": "circular",
        "Kamada-Kawai": "kamada_kawai",
        "Random": "random",
    }

    size_options: dict[str, int | str | None] = {
        "By degree (connections)": "degree",
        "Uniform (8)": 8,
        "Uniform (12)": 12,
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_graph = st.selectbox(
            "Select a graph",
            options=list(graph_options.keys()),
            key="networkx_graph_selector",
        )
    with col2:
        selected_layout = st.selectbox(
            "Layout algorithm",
            options=list(layout_options.keys()),
            key="networkx_layout_selector",
        )
    with col3:
        selected_size = st.selectbox(
            "Node sizing",
            options=list(size_options.keys()),
            key="networkx_size_selector",
        )

    # Load the selected graph
    graph_fn = graph_options[selected_graph]
    graph = graph_fn()
    layout = layout_options[selected_layout]
    node_size = size_options[selected_size]

    # Add labels only for smaller graphs
    if graph.number_of_nodes() <= 100:
        for node in graph.nodes:
            graph.nodes[node]["label"] = str(node)

    st.caption(f"**{graph.number_of_nodes()}** nodes, **{graph.number_of_edges()}** edges")
    sigma_graph(graph, layout=layout, node_size=node_size, height=550)  # type: ignore[arg-type]


__title__ = "Sigma Graph"
__desc__ = "Interactive network graph visualization using sigma.js with WebGL rendering, supporting NetworkX graphs and node-link dictionaries."
__icon__ = "🕸️"
__examples__ = [
    example_basic,
    example_styled,
    example_interactive,
    example_networkx,
]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 4, 9)
