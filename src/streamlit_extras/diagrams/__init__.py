from __future__ import annotations

import base64
import re
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import streamlit as st
import streamlit.components.v2

from .. import extra

if TYPE_CHECKING:
    from diagrams import Diagram as DiagramType

_RESOURCES_DIR = Path(__file__).parent / "resources"
_STREAMLIT_ICON_PATH = str(_RESOURCES_DIR / "streamlit.png")

_DARK_COLOR_MAP = {
    "#2D3436": "#F0F2F6",
    "#7B8894": "#A3ABB5",
}

_DIAGRAM_COMPONENT = st.components.v2.component(
    name="streamlit_extras.diagram",
    html="""
    <style>
        :host {
            overflow: hidden;
        }
        .diagram-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .diagram-container svg {
            display: block;
        }
        .diagram-container.stretch svg {
            width: 100%;
            height: auto;
        }
        .diagram-container.content svg {
            max-width: 100%;
            height: auto;
        }
        .diagram-caption {
            font-size: 0.875rem;
            color: var(--st-secondary-text-color, #6b7280);
            text-align: center;
            margin-top: 0.25rem;
            line-height: 1.4;
        }
    </style>
    <div class="diagram-container" id="diagram-root"></div>
    """,
    js="""
    export default function(component) {
        const { data, parentElement } = component;
        const container = parentElement.querySelector("#diagram-root");
        if (!container) return () => {};

        const svgMarkup = data?.svg ?? "";
        const width = data?.width ?? "stretch";
        const caption = data?.caption ?? "";

        container.className = "diagram-container";
        if (width === "stretch") {
            container.classList.add("stretch");
        } else if (width === "content") {
            container.classList.add("content");
        }

        let html = svgMarkup;

        const host = parentElement.host || parentElement;
        const stFont = getComputedStyle(host).getPropertyValue("--st-font").trim();
        if (stFont) {
            html = html.replaceAll('font-family="Sans-Serif"', 'font-family="' + stFont + '"');
            html = html.replaceAll('font-family="sans-Serif"', 'font-family="' + stFont + '"');
            html = html.replaceAll("font-family='Sans-Serif'", "font-family='" + stFont + "'");
        }

        if (typeof width === "number") {
            html = html.replace(/<svg /, '<svg style="width:' + width + 'px;height:auto;" ');
        }

        if (caption) {
            html += '<div class="diagram-caption">' + caption.replace(/</g, "&lt;").replace(/>/g, "&gt;") + '</div>';
        }

        container.innerHTML = html;

        const svg = container.querySelector("svg");
        if (svg) {
            svg.querySelectorAll("text, text *").forEach(function(el) {
                el.style.fill = "var(--st-text-color)";
            });
            svg.querySelectorAll("path[stroke]").forEach(function(el) {
                const s = el.getAttribute("stroke");
                if (s && s.toLowerCase() === "#7b8894") {
                    el.style.stroke = "var(--st-secondary-text-color, #A3ABB5)";
                }
            });
        }

        return () => {};
    }
    """,
)

_IMAGE_HREF_RE = re.compile(r'xlink:href="([^"]+)"')


def _inline_images(svg: str) -> str:
    def _replacer(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith("data:"):
            return match.group(0)
        p = Path(href)
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            suffix = p.suffix.lstrip(".")
            mime = f"image/{suffix}"
            return f'xlink:href="data:{mime};base64,{b64}"'
        return match.group(0)

    return _IMAGE_HREF_RE.sub(_replacer, svg)


def _is_dark_mode() -> bool:
    try:
        theme = st.context.theme
        if not theme:
            return False
        return theme.get("base") == "dark" or theme.get("type") == "dark"
    except Exception:
        return False


def _swap_colors(text: str) -> str:
    for old, new in _DARK_COLOR_MAP.items():
        text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
    return text


def StreamlitNode(label: str = "Streamlit", **kwargs: object) -> Any:  # noqa: N802
    """Create a Streamlit node for use in ``diagrams`` architecture diagrams.

    This is a convenience wrapper around ``diagrams.custom.Custom`` that
    bundles the Streamlit logo so you don't need to download it yourself.

    Args:
        label: Display label for the node.
        **kwargs: Additional keyword arguments passed to ``Custom``.

    Returns:
        A ``diagrams.custom.Custom`` node instance.
    """
    from diagrams.custom import Custom

    return Custom(label, _STREAMLIT_ICON_PATH, **kwargs)


@extra
def st_diagram(
    diagram: DiagramType,
    *,
    format: Literal["svg", "png"] = "svg",
    width: int | Literal["stretch", "content"] = "stretch",
    caption: str | None = None,
) -> None:
    """Render a ``diagrams`` architecture diagram in Streamlit.

    Args:
        diagram: A ``diagrams.Diagram`` context-manager object
            (use ``show=False`` when creating it).
        format: Output format. ``"svg"`` (default) renders crisp vector
            graphics via a custom component. ``"png"`` uses ``st.image``.
        width: Image width. ``"stretch"`` (default) fills the container,
            ``"content"`` uses the intrinsic size, or pass an ``int`` for
            a fixed pixel width.
        caption: Optional caption displayed below the diagram.
    """
    dot = diagram.dot
    dark = _is_dark_mode()

    saved_graph = dict(dot.graph_attr)
    saved_node = dict(dot.node_attr)
    saved_edge = dict(dot.edge_attr)
    saved_body = list(dot.body)

    dot.graph_attr["bgcolor"] = "transparent"

    if dark:
        for key in ("fontcolor",):
            if key in dot.graph_attr:
                dot.graph_attr[key] = _swap_colors(dot.graph_attr[key])
            if key in dot.node_attr:
                dot.node_attr[key] = _swap_colors(dot.node_attr[key])
        for key in ("color", "fontcolor"):
            if key in dot.edge_attr:
                dot.edge_attr[key] = _swap_colors(dot.edge_attr[key])
        dot.body[:] = [_swap_colors(line) for line in dot.body]

    try:
        raw = dot.pipe(format=format)
    finally:
        dot.graph_attr.clear()
        dot.graph_attr.update(saved_graph)
        dot.node_attr.clear()
        dot.node_attr.update(saved_node)
        dot.edge_attr.clear()
        dot.edge_attr.update(saved_edge)
        dot.body[:] = saved_body

    if format == "png":
        from PIL import Image

        img = Image.open(BytesIO(raw))
        use_cw = width == "stretch"
        kw: dict[str, object] = {"caption": caption, "use_container_width": use_cw}
        if isinstance(width, int):
            kw["width"] = width
        st.image(img, **kw)  # type: ignore[arg-type]
        return

    svg_str = raw.decode("utf-8")
    svg_str = _inline_images(svg_str)

    component_width = width if isinstance(width, str) else "content"
    _DIAGRAM_COMPONENT(
        data={"svg": svg_str, "width": width, "caption": caption or ""},
        width=component_width,
    )


def example() -> None:
    try:
        from diagrams import Diagram
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.aws.network import ELB

        with Diagram(
            "Streamlit App Architecture",
            show=False,
            direction="LR",
            graph_attr={"pad": "0.5", "labelloc": "t"},
        ) as diag:
            StreamlitNode("Frontend") >> ELB("Load Balancer") >> EC2("API Server") >> RDS("Database")

        st_diagram(diag, caption="Built with the diagrams library")
    except ImportError:
        st.warning(
            "This example requires the `diagrams` package and Graphviz. "
            "Install with `pip install diagrams` and [install Graphviz](https://graphviz.org/download/)."
        )


__title__ = "Diagrams"
__desc__ = (
    "Render [mingrammer/diagrams](https://github.com/mingrammer/diagrams) architecture diagrams in Streamlit, "
    "plus a built-in Streamlit node."
)
__icon__ = "📐"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__created_at__ = date(2026, 3, 27)
__github_repo__ = "https://github.com/mingrammer/diagrams"
