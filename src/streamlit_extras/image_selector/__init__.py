from __future__ import annotations

from io import BytesIO
from typing import Literal

import numpy as np
import plotly.graph_objects as go
import requests
import streamlit as st
from PIL import Image, ImageDraw

from streamlit_extras import extra


def convert_to_pil_image(image: str | np.ndarray | Image.Image) -> Image.Image:
    """
    Converts an image from various sources (URL, local path, numpy array, or PIL.Image) to a PIL.Image object.

    Parameters:
    - image: Union[str, np.ndarray, Image.Image]
        The input image which can be:
        - URL (str) pointing to the image
        - Local file path (str)
        - Numpy array (np.ndarray)
        - PIL.Image.Image object

    Returns:
    - Image.Image: The converted PIL.Image object.

    Raises:
    - ValueError: If the input type is not supported or the image cannot be opened.
    """
    if isinstance(image, str):
        if image.startswith("http://") or image.startswith("https://"):
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
) -> dict:
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
        xaxis=dict(showticklabels=False),  # hide x-axis ticks
        yaxis=dict(showticklabels=False),  # hide y-axis ticks
        margin=dict(
            t=0,
            b=5,
        ),
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
    selection: dict,
) -> None:
    """Shows the image selection

    Args:
        image (Image.Image | str | np.ndarray):
            Original image. Can be a PIL object,
            or path to local file, or URL, or NumPy array
        selection (dict): Selection coordinates, output of `image_selector`
    """

    pil_image = convert_to_pil_image(image)
    image_array = np.array(pil_image)

    if coordinates := selection["selection"].get("box"):
        x_min, x_max = coordinates[0]["x"]
        y_min, y_max = coordinates[0]["y"]

        selection_img_array = image_array[
            int(y_min) : int(y_max), int(x_min) : int(x_max)
        ]
        st.image(selection_img_array)

    elif coordinates := selection["selection"].get("lasso"):
        lasso_x, lasso_y = coordinates[0]["x"], coordinates[0]["y"]

        # Create a white background image
        white_background = np.ones_like(image_array) * 255

        # Convert image and coordinates to PIL
        img_pil = Image.fromarray((image_array).astype(np.uint8))
        mask = Image.new("L", (image_array.shape[1], image_array.shape[0]), 0)
        draw = ImageDraw.Draw(mask)
        polygon = list(zip(lasso_x, lasso_y))
        draw.polygon(polygon, outline=1, fill=1)
        mask_array = np.array(mask)

        # Extract the pixels within the lasso selection
        selected_pixels = np.array(img_pil)
        white_background[mask_array == 1] = selected_pixels[mask_array == 1]

        # Extract the bounding box of the polygon
        min_x, min_y = int(min(lasso_x)), int(min(lasso_y))
        max_x, max_y = int(max(lasso_x)), int(max(lasso_y))
        selection_img = Image.fromarray(
            white_background.astype(np.uint8)[min_y:max_y, min_x:max_x]
        )

        # Display the result using Streamlit
        st.image(selection_img)


def example():
    response = requests.get(
        "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
    )

    image = Image.open(BytesIO(response.content))

    selection_type = st.radio(
        "Selection type", ["lasso", "box"], index=0, horizontal=True
    )

    selection = image_selector(image=image, selection_type=selection_type)
    if selection:
        st.json(selection, expanded=False)
        show_selection(image, selection)


__title__ = "Image Selector"
__desc__ = """
Allows users to select an area within an image, using a lasso or a bounding
box."""
__icon__ = "🤠"
__examples__ = {example: [image_selector, show_selection]}
__author__ = "Arnaud Miribel"
__experimental_playground__ = False
__stlite__ = True
