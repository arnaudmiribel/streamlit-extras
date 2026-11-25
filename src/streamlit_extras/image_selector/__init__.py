from __future__ import annotations

from datetime import date
from io import BytesIO
from typing import TYPE_CHECKING, Any, Literal, cast
from unittest import mock

import numpy as np
import plotly.graph_objects as go
import requests
import streamlit as st
from PIL import Image, ImageDraw

from streamlit_extras import extra

if TYPE_CHECKING:
    from streamlit.elements.plotly_chart import PlotlyState


def convert_to_pil_image(image: str | np.ndarray | Image.Image) -> Image.Image:
    """Convert an image from various sources to a PIL.Image object.

    Args:
        image (str | np.ndarray | Image.Image): The input image which can be a URL (str)
            pointing to the image, a local file path (str), a NumPy array (np.ndarray),
            or a PIL.Image.Image object.

    Returns:
        Image.Image: The converted PIL.Image object.

    Raises:
        ValueError: If the input type is not supported or the image cannot be opened.
    """
    pil_image: Image.Image
    if isinstance(image, str):
        if image.startswith(("http://", "https://")):
            response = requests.get(image)
            if response.status_code == 200:
                pil_image = Image.open(BytesIO(response.content))
            else:
                raise ValueError("Could not retrieve image from URL.")
        else:
            pil_image = Image.open(image)
    elif isinstance(image, np.ndarray):
        pil_image = Image.fromarray(image)
    elif isinstance(image, Image.Image):
        pil_image = image
    else:
        raise ValueError("Unsupported image type.")

    return pil_image


@extra
def image_selector(
    image: Image.Image | str | np.ndarray,
    selection_type: Literal["lasso", "box"] = "box",
    key: str = "image-selector",
    width: int = 300,
    height: int = 300,
) -> PlotlyState:
    """Show the image, and enable the user to select an area in
    the image using the provided selection type.

    Args:
        image (Image.Image | str | np.ndarray): Original image. Can be a PIL object,
            or path to local file, or URL, or NumPy array
        selection_type (Literal[["lasso", "box"]): Selection type
        key (str): Key for the st.plotly_chart component. This needs to be unique
            for each instance of `image_selector`. Meaning whenever you call it
            more than once, you should pass a custom `key` for each.
        width (int, optional): Width of the image container. Defaults to 300.
        height (int, optional): Height of the image container. Defaults to 300.

    Returns:
        dict: Selection coordinates
    """

    pil_image = convert_to_pil_image(image)

    fig = go.Figure().add_trace(go.Image(z=pil_image))

    if selection_type == "lasso":
        dragmode = "lasso"
    elif selection_type == "box":
        dragmode = "select"

    fig.update_layout(
        dragmode=dragmode,
        xaxis={"showticklabels": False},  # hide x-axis ticks
        yaxis={"showticklabels": False},  # hide y-axis ticks
        margin={
            "t": 0,
            "b": 5,
        },
        width=width,
        height=height,
    )

    config = {
        "displaylogo": False,
        "displayModeBar": False,
    }

    return st.plotly_chart(fig, on_select="rerun", config=config, key=key)


@extra
def show_selection(
    image: Image.Image | str | np.ndarray,
    selection: PlotlyState,
) -> None:
    """Shows the image selection

    Args:
        image (Image.Image | str | np.ndarray):
            Original image. Can be a PIL object,
            or path to local file, or URL, or NumPy array
        selection (PlotlyState): Selection coordinates, output of `image_selector`
    """

    pil_image = convert_to_pil_image(image)
    image_array = np.array(pil_image)

    if coordinates := selection["selection"].get("box"):
        x_min, x_max = sorted(coordinates[0]["x"])
        y_min, y_max = sorted(coordinates[0]["y"])

        selection_img_array = image_array[int(y_min) : int(y_max), int(x_min) : int(x_max)]
        st.image(selection_img_array)

    elif coordinates := selection["selection"].get("lasso"):
        lasso_x, lasso_y = coordinates[0]["x"], coordinates[0]["y"]

        # Create a white background image
        white_background = np.ones_like(image_array) * 255

        # Convert image and coordinates to PIL
        img_pil = Image.fromarray((image_array).astype(np.uint8))
        mask = Image.new("L", (image_array.shape[1], image_array.shape[0]), 0)
        draw = ImageDraw.Draw(mask)
        polygon = list(zip(lasso_x, lasso_y, strict=False))
        draw.polygon(polygon, outline=1, fill=1)
        mask_array = np.array(mask)

        # Extract the pixels within the lasso selection
        selected_pixels = np.array(img_pil)
        white_background[mask_array == 1] = selected_pixels[mask_array == 1]

        # Extract the bounding box of the polygon
        min_x, min_y = int(min(lasso_x)), int(min(lasso_y))
        max_x, max_y = int(max(lasso_x)), int(max(lasso_y))
        selection_img = Image.fromarray(white_background.astype(np.uint8)[min_y:max_y, min_x:max_x])

        # Display the result using Streamlit
        st.image(selection_img)


def example() -> None:
    response = requests.get(
        "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
    )

    image = Image.open(BytesIO(response.content))

    selection_type = st.radio("Selection type", ["lasso", "box"], index=0, horizontal=True)

    selection = image_selector(image=image, selection_type=cast("Literal['lasso', 'box']", selection_type))
    if selection:
        st.json(selection, expanded=False)
        show_selection(image, selection)


def _get_box_crop_shape(x: list[float], y: list[float]) -> tuple[int, ...]:
    """Build a fake box-selection PlotlyState and return the shape of the
    crop that `show_selection` would pass to `st.image`.

    Returns:
        tuple[int, ...]: Shape of the array that would be displayed.
    """
    image_array = np.zeros((100, 100, 3), dtype=np.uint8)
    selection: PlotlyState = {
        "selection": {
            "points": [],
            "point_indices": [],
            "box": [{"x": x, "y": y}],
            "lasso": [],
        }
    }

    with mock.patch("streamlit_extras.image_selector.st.image") as mock_st_image:
        show_selection(image_array, selection)

    displayed_array = mock_st_image.call_args[0][0]
    return cast("tuple[int, ...]", displayed_array.shape)


def test_box_selection_forward_drag() -> None:
    # Dragging top-left -> bottom-right already yields (min, max) order.
    assert _get_box_crop_shape(x=[10, 90], y=[20, 80]) == (60, 80, 3)


def test_box_selection_reversed_drag() -> None:
    # Dragging bottom-right -> top-left yields (max, min) order. Regression
    # test for https://github.com/arnaudmiribel/streamlit-extras/issues/269:
    # the crop shape must match the forward-drag equivalent instead of
    # raising "zero-size array to reduction operation minimum which has no
    # identity".
    assert _get_box_crop_shape(x=[90, 10], y=[80, 20]) == (60, 80, 3)


__title__ = "Image Selector"
__desc__ = """
Allows users to select an area within an image, using a lasso or a bounding
box."""
__icon__ = "🤠"
__examples__ = {example: [image_selector, show_selection]}
__author__ = "Arnaud Miribel"
__created_at__ = date(2024, 8, 1)
__experimental_playground__ = False
__stlite__ = True
__tests__ = [test_box_selection_forward_drag, test_box_selection_reversed_drag]
