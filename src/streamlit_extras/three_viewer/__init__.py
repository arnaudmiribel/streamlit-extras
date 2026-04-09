"""3D model viewer for Streamlit using Three.js.

Display 3D models (GLTF, GLB, OBJ, STL, PLY, FBX) with interactive orbit controls.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from io import BufferedReader, BytesIO, RawIOBase
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import streamlit as st
import streamlit.components.v2
from streamlit import runtime

from streamlit_extras import extra

if TYPE_CHECKING:
    from collections.abc import Callable

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


# Supported file extensions (must match frontend loaders)
_SUPPORTED_FORMATS: frozenset[str] = frozenset(_MIME_TYPES.keys())


def _get_file_extension(filename: str) -> str:
    """Extract the file extension from a filename or URL.

    Returns:
        The lowercase file extension including the leading dot.
    """
    # Handle URLs by extracting the path - strip query params and fragments
    if "?" in filename:
        filename = filename.split("?", maxsplit=1)[0]
    if "#" in filename:
        filename = filename.split("#", maxsplit=1)[0]
    return Path(filename).suffix.lower()


def _add_to_media_file_manager(data: bytes, mime_type: str) -> str:
    """Add data to Streamlit's media file manager.

    Args:
        data: The binary data to add.
        mime_type: The MIME type of the data.

    Returns:
        The URL to access the file.

    Raises:
        RuntimeError: If the Streamlit version is incompatible.
    """
    rt = runtime.get_instance()

    # Prefer the current behavior using Streamlit's internal delta path API.
    # This relies on a private attribute and may break in future versions,
    # so we wrap it in a try/except and provide a compatibility fallback.
    try:
        coordinates = st._main._get_delta_path_str()
    except Exception:
        media_mgr = rt.media_file_mgr
        # Fallback: try calling without explicit coordinates (if supported in older Streamlit).
        # Cast bypasses type checker - this call is intentionally incorrect and will fail
        # with TypeError on current Streamlit versions, caught by the except block below.
        try:
            add_fn = cast("Callable[[bytes, str], str]", media_mgr.add)
            return add_fn(data, mime_type)
        except TypeError as exc:
            msg = (
                "Incompatible Streamlit version detected: unable to access "
                "internal API 'st._main._get_delta_path_str', and "
                "media_file_mgr.add(...) requires explicit coordinates. "
                "Please upgrade/downgrade Streamlit to a compatible version "
                "or report this issue to the maintainers of "
                "streamlit-extras.three_viewer."
            )
            raise RuntimeError(msg) from exc
    else:
        return rt.media_file_mgr.add(data, mime_type, coordinates)


def _process_source(
    source: str | Path | bytes | BytesIO | RawIOBase | BufferedReader,
    file_format: str | None = None,
) -> tuple[str, str]:
    """Process the source and return (url, format).

    For URLs, returns the URL directly.
    For local files and bytes, uploads to Streamlit's media file manager.

    Args:
        source: The 3D model source.
        file_format: Explicit format override (e.g., ".glb", ".stl").
            Required for bytes/BytesIO inputs with non-GLB formats.

    Returns:
        Tuple of (url, format_extension).

    Raises:
        TypeError: If the source type is not supported.
    """
    # Handle URL strings
    if isinstance(source, str):
        if source.startswith(("http://", "https://")):
            ext = file_format or _get_file_extension(source)
            return source, ext

        # Treat as file path
        source = Path(source)

    # Handle Path objects
    if isinstance(source, Path):
        ext = file_format or source.suffix.lower()
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
        # Use explicit format or default to GLB for binary data
        ext = file_format or ".glb"
        mime_type = _MIME_TYPES.get(ext, "application/octet-stream")
        url = _add_to_media_file_manager(data, mime_type)
        return url, ext

    # Handle raw bytes
    if isinstance(source, bytes):
        # Use explicit format or default to GLB for raw bytes
        ext = file_format or ".glb"
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
    file_format: str | None = None,
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
        file_format: Explicit format override (e.g., ".glb", ".stl", ".obj").
            Required for bytes/BytesIO inputs with non-GLB formats.
            If not provided, the format is inferred from the source.
        height: Height of the viewer in pixels.
        key: Unique key for this component instance.

    Returns:
        The Streamlit DeltaGenerator for this component.

    Example:

        ```python
        three_viewer("model.glb")
        three_viewer("https://example.com/model.gltf", height=600)
        three_viewer(stl_bytes, file_format=".stl")
        ```
    """
    # Normalize format if provided
    normalized_format = None
    if file_format is not None:
        normalized_format = file_format.lower()
        if not normalized_format.startswith("."):
            normalized_format = "." + normalized_format

    url, detected_format = _process_source(source, normalized_format)

    # Use normalized format if provided, otherwise use detected format
    final_format = normalized_format or detected_format

    # Validate the format
    if final_format and final_format not in _SUPPORTED_FORMATS:
        supported = ", ".join(sorted(_SUPPORTED_FORMATS))
        st.exception(ValueError(f"Unsupported 3D model format: '{final_format}'. Supported formats are: {supported}"))
        # Return empty component to avoid frontend crash
        return st.empty()

    component = _get_component()
    return component(
        key=key,
        data={
            "url": url,
            "format": final_format,
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
__desc__ = "Display 3D models (GLTF, GLB, OBJ, STL, PLY, FBX) with interactive orbit controls using Three.js."
__icon__ = "🎮"
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 3, 25)
__examples__ = [example_basic, example_with_options]


# Unit tests for helper functions
def _test_get_file_extension_basic() -> None:
    """Test basic extension extraction."""
    assert _get_file_extension("model.glb") == ".glb"
    assert _get_file_extension("path/to/model.GLTF") == ".gltf"
    assert _get_file_extension("model.stl") == ".stl"


def _test_get_file_extension_urls() -> None:
    """Test extension extraction from URLs with query params and fragments."""
    assert _get_file_extension("https://example.com/model.glb?v=1") == ".glb"
    assert _get_file_extension("https://example.com/model.glb#section") == ".glb"
    assert _get_file_extension("https://example.com/model.glb?v=1#section") == ".glb"
    assert _get_file_extension("https://example.com/model.obj?token=abc&v=2") == ".obj"


def _test_get_file_extension_no_extension() -> None:
    """Test files without extensions."""
    assert not _get_file_extension("model")
    assert not _get_file_extension("https://example.com/model")


def _test_supported_formats() -> None:
    """Test that all MIME types have corresponding supported formats."""
    assert ".glb" in _SUPPORTED_FORMATS
    assert ".gltf" in _SUPPORTED_FORMATS
    assert ".obj" in _SUPPORTED_FORMATS
    assert ".stl" in _SUPPORTED_FORMATS
    assert ".ply" in _SUPPORTED_FORMATS
    assert ".fbx" in _SUPPORTED_FORMATS


__tests__ = [
    _test_get_file_extension_basic,
    _test_get_file_extension_urls,
    _test_get_file_extension_no_extension,
    _test_supported_formats,
]
