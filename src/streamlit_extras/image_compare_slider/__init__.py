"""Interactive image comparison slider for Streamlit.

A slider component that allows comparing two images side-by-side with a draggable
divider. Commonly used for before/after comparisons, image quality comparisons,
and visual diffs.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import TYPE_CHECKING, Any, Literal
from uuid import uuid4

import streamlit as st
import streamlit.components.v2
from streamlit.elements.lib.image_utils import image_to_url
from streamlit.elements.lib.layout_utils import LayoutConfig
from streamlit.errors import StreamlitAPIException

from streamlit_extras import extra

if TYPE_CHECKING:
    from io import BytesIO
    from pathlib import Path

    import numpy.typing as npt
    from PIL import Image

    ImageLike = str | bytes | BytesIO | Path | Image.Image | npt.NDArray[Any]


def _on_position_change() -> None:
    """Callback function for when the slider position changes."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.image_compare_slider",
        js="index-*.js",
        html='<div class="react-root"></div>',
    )


def _convert_image_to_url(image: ImageLike) -> str:
    """Convert an image to a URL that can be served by Streamlit.

    Returns:
        A URL string that Streamlit can serve.
    """
    image_id = str(uuid4())
    return image_to_url(
        image,
        layout_config=LayoutConfig(width="content"),
        clamp=False,
        channels="RGB",
        output_format="auto",
        image_id=image_id,
    )


@extra
def image_compare_slider(
    image1: ImageLike,
    image2: ImageLike,
    *,
    label1: str | None = None,
    label2: str | None = None,
    position: float = 0.5,
    portrait: bool = False,
    height: Literal["content"] | int = "content",
    width: Literal["stretch", "content"] | int = "stretch",
    key: str | None = None,
) -> float:
    """Display an interactive image comparison slider.

    Overlays two images with a draggable divider that reveals portions of each.
    Useful for before/after comparisons, quality comparisons, and visual diffs.

    Args:
        image1: The first (left or top) image. Supports URLs (str), file paths
            (str or Path), PIL images, numpy arrays, or raw bytes/BytesIO.
        image2: The second (right or bottom) image. Same formats as image1.
        label1: Optional label displayed over the first image.
        label2: Optional label displayed over the second image.
        position: Initial slider position as a value between 0 and 1. Default is 0.5.
        portrait: If True, slider moves vertically (top/bottom comparison).
            Default is False (horizontal left/right comparison).
        height: Component height. "content" (default) auto-sizes based on image
            aspect ratio. Integer sets fixed pixel height.
        width: Component width. "stretch" (default) fills container width.
            "content" sizes to fit content. Integer sets fixed pixel width.
        key: Unique key for this component instance.

    Returns:
        Current slider position as a value between 0 and 1.

    Raises:
        StreamlitAPIException: If position is not between 0 and 1.

    Example:
        Basic comparison:

        ```python
        image_compare_slider("before.jpg", "after.jpg")
        ```

        With labels:

        ```python
        image_compare_slider(
            "original.png",
            "edited.png",
            label1="Original",
            label2="Edited",
        )
        ```

        Vertical comparison:

        ```python
        image_compare_slider(
            "top.jpg",
            "bottom.jpg",
            portrait=True,
        )
        ```
    """
    # Validate position
    if not 0 <= position <= 1:
        raise StreamlitAPIException(f"position must be between 0 and 1, got {position}.")

    # Validate height
    if isinstance(height, int) and height < 1:
        raise StreamlitAPIException(f"height must be at least 1 pixel, got {height}.")
    if not isinstance(height, int) and height != "content":
        raise StreamlitAPIException(f"height must be 'content' or an integer, got {height!r}.")

    # Validate width
    if isinstance(width, int) and width < 1:
        raise StreamlitAPIException(f"width must be at least 1 pixel, got {width}.")
    if not isinstance(width, int) and width not in ("stretch", "content"):
        raise StreamlitAPIException(f"width must be 'stretch', 'content', or an integer, got {width!r}.")

    # Convert images to URLs
    image1_url = _convert_image_to_url(image1)
    image2_url = _convert_image_to_url(image2)

    # Convert position to percentage (0-100) for the frontend
    position_percent = position * 100

    component = _get_component()
    result = component(
        key=key,
        data={
            "image1_url": image1_url,
            "image2_url": image2_url,
            "label1": label1 or "",
            "label2": label2 or "",
            "portrait": portrait,
            "height": height,
            "width": width,
            "initial_position": position_percent,
        },
        default={"position": position_percent},
        on_position_change=_on_position_change,
        height=height,
        width=width,
    )

    # Get the current position from the result (in percentage) and convert to 0-1
    current_position_percent: float = result.get("position", position_percent)

    # Convert back to 0-1 range and clamp
    return max(0.0, min(1.0, current_position_percent / 100))


def example_basic() -> None:
    """Basic before/after comparison."""
    st.write("### Basic Comparison")
    st.write("Drag the slider to compare the two images.")

    position = image_compare_slider(
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&sat=-100",
        label1="Color",
        label2="Grayscale",
        key="basic_compare",
    )
    st.write(f"Slider position: **{position:.2f}**")


def example_portrait() -> None:
    """Vertical (portrait) comparison mode."""
    st.write("### Portrait Mode")
    st.write("Vertical slider for top/bottom comparison.")

    image_compare_slider(
        "https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=600",
        "https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=600&blur=10",
        label1="Sharp",
        label2="Blurred",
        portrait=True,
        key="portrait_compare",
    )


def example_custom_position() -> None:
    """Custom starting position."""
    st.write("### Custom Start Position")

    start_pos = st.slider("Starting position", 0.0, 1.0, 0.25, key="start_pos_slider")

    image_compare_slider(
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&con=2",
        label1="Normal",
        label2="High Contrast",
        position=start_pos,
        key="custom_pos_compare",
    )


__title__ = "Image Compare Slider"
__desc__ = "Compare two images with an interactive slider overlay."
__icon__ = "🔀"
__examples__ = [
    example_basic,
    example_portrait,
    example_custom_position,
]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 4, 9)
