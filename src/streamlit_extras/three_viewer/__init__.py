"""3D model viewer for Streamlit using Three.js.

Display 3D models (GLTF, GLB, OBJ, STL, PLY) with interactive orbit controls.
"""

from __future__ import annotations

from functools import cache
from io import BufferedReader, BytesIO, RawIOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any

import streamlit as st
import streamlit.components.v2
from streamlit import runtime

from streamlit_extras import extra

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


# MIME types for 3D model formats
_MIME_TYPES: dict[str, str] = {
    ".gltf": "model/gltf+json",
    ".glb": "model/gltf-binary",
    ".obj": "text/plain",
    ".stl": "model/stl",
    ".ply": "application/x-ply",
    ".fbx": "application/octet-stream",
}


def _get_file_extension(filename: str) -> str:
    """Extract the file extension from a filename or URL.

    Returns:
        The lowercase file extension including the leading dot.
    """
    # Handle URLs by extracting the path
    if "?" in filename:
        filename = filename.split("?", maxsplit=1)[0]
    return Path(filename).suffix.lower()


def _add_to_media_file_manager(data: bytes, mime_type: str) -> str:
    """Add data to Streamlit's media file manager.

    Args:
        data: The binary data to add.
        mime_type: The MIME type of the data.

    Returns:
        The URL to access the file.
    """
    coordinates = st._main._get_delta_path_str()
    return runtime.get_instance().media_file_mgr.add(data, mime_type, coordinates)


def _process_source(
    source: str | Path | bytes | BytesIO | RawIOBase | BufferedReader,
) -> tuple[str, str]:
    """Process the source and return (url, format).

    For URLs, returns the URL directly.
    For local files and bytes, uploads to Streamlit's media file manager.

    Args:
        source: The 3D model source.

    Returns:
        Tuple of (url, format_extension).

    Raises:
        TypeError: If the source type is not supported.
    """
    # Handle URL strings
    if isinstance(source, str):
        if source.startswith(("http://", "https://")):
            ext = _get_file_extension(source)
            return source, ext

        # Treat as file path
        source = Path(source)

    # Handle Path objects
    if isinstance(source, Path):
        ext = source.suffix.lower()
        data = Path(source).read_bytes()
        mime_type = _MIME_TYPES.get(ext, "application/octet-stream")
        url = _add_to_media_file_manager(data, mime_type)
        return url, ext

    # Handle BytesIO and other IO objects
    if isinstance(source, (BytesIO, RawIOBase, BufferedReader)):
        # Use isinstance check to satisfy both type checkers (noqa for ruff SIM108)
        if isinstance(source, BytesIO):  # noqa: SIM108
            data = source.getvalue()
        else:
            data = source.read()
        # Default to GLB for binary data without extension info
        ext = ".glb"
        mime_type = _MIME_TYPES.get(ext, "application/octet-stream")
        url = _add_to_media_file_manager(data, mime_type)
        return url, ext

    # Handle raw bytes
    if isinstance(source, bytes):
        # Default to GLB for raw bytes
        ext = ".glb"
        mime_type = _MIME_TYPES.get(ext, "application/octet-stream")
        url = _add_to_media_file_manager(source, mime_type)
        return url, ext

    msg = f"Unsupported source type: {type(source)}"
    raise TypeError(msg)


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.three_viewer",
        js="index-*.js",
        html='<div class="three-root"></div>',
    )


@extra
def three_viewer(
    source: str | Path | bytes | BytesIO | RawIOBase | BufferedReader,
    *,
    height: int = 400,
    key: str | None = None,
) -> DeltaGenerator:
    """Display a 3D model using Three.js with interactive orbit controls.

    Supports common 3D formats including GLTF/GLB (recommended), OBJ, STL, PLY, and FBX.

    Args:
        source: The 3D model to display. Can be:
            - A URL (http:// or https://)
            - A local file path (str or Path)
            - Binary data (bytes)
            - A BytesIO or file-like object
        height: Height of the viewer in pixels.
        key: Unique key for this component instance.

    Returns:
        The Streamlit DeltaGenerator for this component.

    Example:
        >>> three_viewer("model.glb")
        >>> three_viewer("https://example.com/model.gltf", height=600)
    """
    url, file_format = _process_source(source)

    component = _get_component()
    return component(
        key=key,
        data={
            "url": url,
            "format": file_format,
            "height": height,
        },
    )


def example_basic() -> None:
    """Basic 3D viewer demo with a sample model."""
    st.write("### Basic 3D Viewer")
    st.write("Display a 3D model from a URL with orbit controls.")

    # Using a public GLB model from the Khronos glTF sample models
    model_url = (
        "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Duck/glTF-Binary/Duck.glb"
    )

    three_viewer(model_url, height=400, key="basic_demo")

    st.caption("Drag to rotate, scroll to zoom, right-click drag to pan.")


def example_with_options() -> None:
    """Interactive demo with configurable height."""
    st.write("### Configurable Height")

    height = st.slider("Viewer height", min_value=200, max_value=800, value=400, step=50)

    model_url = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/BoxAnimated/glTF-Binary/BoxAnimated.glb"
    three_viewer(model_url, height=height, key="options_demo")


__title__ = "Three.js 3D Viewer"
__desc__ = "Display 3D models (GLTF, GLB, OBJ, STL, PLY) with interactive orbit controls using Three.js."
__icon__ = "🎮"
__author__ = "streamlit-extras"
__examples__ = [example_basic, example_with_options]
__streamlit_min_version__ = "1.46.0"
