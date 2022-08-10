import base64
import io
import os
import uuid

import sahi.utils.cv
import streamlit.components.v1 as components
from PIL import Image

__version__ = "0.0.2"

TEMP_DIR = "temp"


def pillow_to_base64(image: Image.Image):
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format="JPEG", subsampling=0, quality=100)
    img_bytes = in_mem_file.getvalue()  # bytes
    image_str = base64.b64encode(img_bytes).decode("utf-8")
    base64_src = f"data:image/jpg;base64,{image_str}"
    return base64_src


def local_file_to_base64(image_path: str):
    file_ = open(image_path, "rb")
    img_bytes = file_.read()
    image_str = base64.b64encode(img_bytes).decode("utf-8")
    file_.close()
    base64_src = f"data:image/jpg;base64,{image_str}"
    return base64_src


def pillow_local_file_to_base64(image: Image.Image):
    # pillow to local file
    img_path = TEMP_DIR + "/" + str(uuid.uuid4()) + ".jpg"
    image.save(img_path, subsampling=0, quality=100)
    # local file base64 str
    base64_src = local_file_to_base64(img_path)
    return base64_src


def image_comparison(
    img1: str,
    img2: str,
    label1: str = "1",
    label2: str = "2",
    width: int = 700,
    show_labels: bool = True,
    starting_position: int = 50,
    make_responsive: bool = True,
    in_memory=False,
):
    """Create a new juxtapose component.
    Parameters
    ----------
    img1: str, PosixPath, PIL.Image or URL
        Input image to compare
    img2: str, PosixPath, PIL.Image or URL
        Input image to compare
    label1: str or None
        Label for image 1
    label2: str or None
        Label for image 2
    width: int or None
        Width of the component in px
    show_labels: bool or None
        Show given labels on images
    starting_position: int or None
        Starting position of the slider as percent (0-100)
    make_responsive: bool or None
        Enable responsive mode
    in_memory: bool or None
        Handle pillow to base64 conversion in memory without saving to local
    Returns
    -------
    static_component: Boolean
        Returns a static component with a timeline
    """
    # prepare images
    img1_pillow = sahi.utils.cv.read_image_as_pil(img1)
    img2_pillow = sahi.utils.cv.read_image_as_pil(img2)

    img_width, img_height = img1_pillow.size
    h_to_w = img_height / img_width
    height = (width * h_to_w) * 0.95

    if in_memory:
        # create base64 str from pillow images
        img1 = pillow_to_base64(img1_pillow)
        img2 = pillow_to_base64(img2_pillow)
    else:
        # clean temp dir
        os.makedirs(TEMP_DIR, exist_ok=True)
        for file_ in os.listdir(TEMP_DIR):
            if file_.endswith(".jpg"):
                os.remove(TEMP_DIR + "/" + file_)
        # create base64 str from pillow images
        img1 = pillow_local_file_to_base64(img1_pillow)
        img2 = pillow_local_file_to_base64(img2_pillow)

    # load css + js
    cdn_path = "https://cdn.knightlab.com/libs/juxtapose/latest"
    css_block = f'<link rel="stylesheet" href="{cdn_path}/css/juxtapose.css">'
    js_block = f'<script src="{cdn_path}/js/juxtapose.min.js"></script>'

    # write html block
    htmlcode = f"""
        {css_block}
        {js_block}
        <div id="foo"style="height: {height}; width: {width or '%100'};"></div>
        <script>
        slider = new juxtapose.JXSlider('#foo',
            [
                {{
                    src: '{img1}',
                    label: '{label1}',
                }},
                {{
                    src: '{img2}',
                    label: '{label2}',
                }}
            ],
            {{
                animate: true,
                showLabels: {'true' if show_labels else 'false'},
                showCredits: true,
                startingPosition: "{starting_position}%",
                makeResponsive: {'true' if make_responsive else 'false'},
            }});
        </script>
        """
    static_component = components.html(htmlcode, height=height, width=width)

    return static_component


def example():
    image_comparison(
        img1="https://user-images.githubusercontent.com/34196005/143309873-c0c1f31c-c42e-4a36-834e-da0a2336bb19.jpg",
        img2="https://user-images.githubusercontent.com/34196005/143309867-42841f5a-9181-4d22-b570-65f90f2da231.jpg",
        label1="YOLOX",
        label2="SAHI+YOLOX",
        width=700,
        starting_position=50,
        show_labels=True,
        make_responsive=True,
        in_memory=True,
    )
