"""Interactive image cropping component for Streamlit.

A component that allows users to select a rectangular crop region on an image,
returning the bounds as percentages. Commonly used for photo editing, avatar
selection, and annotation workflows.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import TYPE_CHECKING, Any, Literal, TypedDict
from uuid import uuid4

import streamlit as st
import streamlit.components.v2
from streamlit.elements.lib.image_utils import image_to_url
from streamlit.elements.lib.layout_utils import LayoutConfig
from streamlit.errors import StreamlitAPIException

from streamlit_extras import extra

if TYPE_CHECKING:
    from collections.abc import Callable
    from io import BytesIO
    from pathlib import Path

    import numpy.typing as npt
    from PIL import Image

    ImageLike = str | bytes | BytesIO | Path | Image.Image | npt.NDArray[Any]


class CropBounds(TypedDict):
    """Crop bounds as normalized values (0-1)."""

    x: float
    y: float
    width: float
    height: float


def _on_crop_change() -> None:
    """Callback function for when the crop region changes."""


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.image_crop",
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
def image_crop(
    image: ImageLike,
    *,
    aspect: float | None = None,
    min_width: int = 10,
    min_height: int = 10,
    initial_crop: CropBounds | None = None,
    circular: bool = False,
    rule_of_thirds: bool = False,
    height: Literal["content"] | int = "content",
    width: Literal["stretch", "content"] | int = "stretch",
    on_change: Literal["ignore", "rerun"] | Callable[[], None] = "rerun",
    key: str | None = None,
) -> CropBounds | None:
    """Display an interactive image cropping component.

    Allows users to select a rectangular region on an image by clicking and
    dragging. Returns the crop bounds as normalized values (0-1).

    Args:
        image: The image to crop. Supports URLs (str), file paths (str or Path),
            PIL images, numpy arrays, or raw bytes/BytesIO.
        aspect: Fixed aspect ratio for the crop selection (e.g., 1 for square,
            16/9 for landscape). None allows free-form selection.
        min_width: Minimum crop width in pixels. Default is 10.
        min_height: Minimum crop height in pixels. Default is 10.
        initial_crop: Initial crop selection as a CropBounds dict with x, y,
            width, and height as normalized values (0-1). None shows no initial
            selection.
        circular: If True, displays a circular mask over the selection. The
            returned bounds are still rectangular. Default is False.
        rule_of_thirds: If True, displays composition guideline grid.
            Default is False.
        height: Component height. "content" (default) auto-sizes based on image
            aspect ratio. Integer sets fixed pixel height.
        width: Component width. "stretch" (default) fills container width.
            "content" sizes to fit content. Integer sets fixed pixel width.
        on_change: Controls behavior when the crop region changes.
            "rerun" (default): Triggers a script rerun, returns the crop bounds.
            "ignore": No rerun, always returns None.
            Callable: Calls the provided callback, returns the crop bounds.
        key: Unique key for this component instance.

    Returns:
        CropBounds dict with x, y, width, and height as normalized values (0-1)
        when a selection exists and on_change is not "ignore". Returns None
        when no selection is active or on_change is "ignore".

    Raises:
        StreamlitAPIException: If parameters are invalid.

    Example:
        Basic cropping:

        ```python
        crop = image_crop("photo.jpg")
        if crop:
            st.write(f"Selected: {crop}")
        ```

        Square avatar selection:

        ```python
        crop = image_crop(
            image,
            aspect=1,
            circular=True,
        )
        ```
    """
    # Validate aspect
    if aspect is not None and aspect <= 0:
        raise StreamlitAPIException(f"aspect must be positive, got {aspect}.")

    # Validate min dimensions
    if min_width < 1:
        raise StreamlitAPIException(f"min_width must be at least 1, got {min_width}.")
    if min_height < 1:
        raise StreamlitAPIException(f"min_height must be at least 1, got {min_height}.")

    # Validate initial_crop
    if initial_crop is not None:
        for field in ("x", "y", "width", "height"):
            if field not in initial_crop:
                raise StreamlitAPIException(f"initial_crop must contain '{field}' key.")
            value = initial_crop[field]
            # Reject bools (which are technically ints in Python)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise StreamlitAPIException(f"initial_crop['{field}'] must be a number, got {type(value).__name__}.")

        # Validate ranges (0-1 normalized values)
        x = initial_crop["x"]
        y = initial_crop["y"]
        crop_width = initial_crop["width"]
        crop_height = initial_crop["height"]

        if not 0 <= x <= 1:
            raise StreamlitAPIException(f"initial_crop['x'] must be between 0 and 1, got {x}.")
        if not 0 <= y <= 1:
            raise StreamlitAPIException(f"initial_crop['y'] must be between 0 and 1, got {y}.")
        if not 0 < crop_width <= 1:
            raise StreamlitAPIException(
                f"initial_crop['width'] must be greater than 0 and at most 1, got {crop_width}."
            )
        if not 0 < crop_height <= 1:
            raise StreamlitAPIException(
                f"initial_crop['height'] must be greater than 0 and at most 1, got {crop_height}."
            )
        if x + crop_width > 1:
            raise StreamlitAPIException(
                f"initial_crop['x'] + initial_crop['width'] must be at most 1, got {x + crop_width}."
            )
        if y + crop_height > 1:
            raise StreamlitAPIException(
                f"initial_crop['y'] + initial_crop['height'] must be at most 1, got {y + crop_height}."
            )

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

    # Validate on_change parameter
    if on_change not in ("ignore", "rerun") and not callable(on_change):
        raise StreamlitAPIException(f"on_change must be 'ignore', 'rerun', or a callable, got {on_change!r}.")

    # Convert image to URL
    image_url = _convert_image_to_url(image)

    # Prepare initial crop for frontend (convert 0-1 to 0-100 for react-image-crop)
    frontend_initial_crop = None
    if initial_crop is not None:
        frontend_initial_crop = {
            "x": max(0, min(100, initial_crop["x"] * 100)),
            "y": max(0, min(100, initial_crop["y"] * 100)),
            "width": max(0, min(100, initial_crop["width"] * 100)),
            "height": max(0, min(100, initial_crop["height"] * 100)),
        }

    # Determine if we should track crop changes
    track_crop = on_change != "ignore"

    # Build component kwargs
    component_kwargs: dict[str, Any] = {
        "key": key,
        "data": {
            "image_url": image_url,
            "aspect": aspect,
            "min_width": min_width,
            "min_height": min_height,
            "initial_crop": frontend_initial_crop,
            "circular": circular,
            "rule_of_thirds": rule_of_thirds,
            "height": height,
            "width": width,
            "track_crop": track_crop,
        },
        "height": height,
        "width": width,
    }

    # Only add callback and default if tracking crop
    if track_crop:
        component_kwargs["default"] = {"crop": frontend_initial_crop}
        if callable(on_change):
            component_kwargs["on_crop_change"] = on_change
        else:  # on_change == "rerun"
            component_kwargs["on_crop_change"] = _on_crop_change

    component = _get_component()
    result = component(**component_kwargs)

    # Return None when ignoring changes
    if on_change == "ignore":
        return None

    # Get the current crop from the result
    current_crop = result.get("crop")

    if current_crop is None:
        return None

    # Helper to safely get and normalize a crop value
    def get_normalized(key: str) -> float:
        value = current_crop.get(key)
        if value is None or not isinstance(value, (int, float)):
            return 0.0
        # Convert from 0-100 (frontend) to 0-1 (API) and clamp
        return max(0.0, min(1.0, float(value) / 100))

    # Convert from 0-100 (frontend) to 0-1 (API) and return as CropBounds
    return CropBounds(
        x=get_normalized("x"),
        y=get_normalized("y"),
        width=get_normalized("width"),
        height=get_normalized("height"),
    )


def example_basic() -> None:
    """Basic image cropping."""
    st.write("### Basic Cropping")
    st.write("Click and drag on the image to select a crop region.")

    crop = image_crop(
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        key="basic_crop",
    )
    if crop:
        st.write(
            f"**Selected region:** x={crop['x']:.2f}, y={crop['y']:.2f}, "
            f"width={crop['width']:.2f}, height={crop['height']:.2f}"
        )
    else:
        st.write("No region selected yet.")


def example_square() -> None:
    """Square aspect ratio cropping."""
    st.write("### Square Crop")
    st.write("Fixed 1:1 aspect ratio for avatar-style selection.")

    crop = image_crop(
        "https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=600",
        aspect=1,
        initial_crop={"x": 0.25, "y": 0.1, "width": 0.5, "height": 0.5},
        key="square_crop",
    )
    if crop:
        st.write(f"**Crop bounds:** {crop}")


def example_circular() -> None:
    """Circular crop mask."""
    st.write("### Circular Mask")
    st.write("Circular display for profile picture selection.")

    crop = image_crop(
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800",
        aspect=1,
        circular=True,
        key="circular_crop",
    )
    if crop:
        st.write(f"**Crop bounds:** {crop}")


def example_composition() -> None:
    """Composition helper with rule of thirds."""
    st.write("### Composition Helper")
    st.write("Rule of thirds grid for photo composition.")

    crop = image_crop(
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        aspect=16 / 9,
        rule_of_thirds=True,
        key="composition_crop",
    )
    if crop:
        st.write(f"**16:9 crop:** {crop}")


__title__ = "Image Crop"
__desc__ = "Interactive image cropping with adjustable bounds."
__icon__ = "✂️"
__examples__ = [
    example_basic,
    example_square,
    example_circular,
    example_composition,
]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 4, 14)
