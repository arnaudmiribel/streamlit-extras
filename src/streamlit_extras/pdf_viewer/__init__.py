from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Union

import numpy.typing as npt
import streamlit as st

from .. import extra

PdfData = Union[
    str,
    Path,
    bytes,
    io.BytesIO,
    io.RawIOBase,
    io.BufferedReader,
    "npt.NDArray[Any]",
    None,
]


@extra
def pdf_viewer(
    data: PdfData,
    width: int | None = None,
    height: int | None = None,
    *,
    scrolling: bool = True,
) -> None:
    """Display a PDF document.

    Args:
        data (str, Path, bytes, io.BytesIO, or file): The PDF to display. This can be one of the following:
            - A URL (string) for a hosted PDF file.
            - A path to a local PDF file. The path can be a ``str``
            or ``Path`` object. Paths can be absolute or relative to the
            working directory (where you execute ``streamlit run``).
            - Raw PDF data. Raw data formats must include all necessary file
            headers for a valid PDF document.

        width (int or None): The width of the PDF viewer in CSS pixels. By default, this uses the full
            container width.

        height (int or None): The height of the PDF viewer in CSS pixels. Defaults to 500.

        scrolling (bool): Whether to allow scrolling in the PDF viewer. If this is ``True``
            (default), Streamlit shows a scrollbar when the content is larger
            than the iframe. If this is ``False``, Streamlit crops any content
            larger than the iframe and does not show a scrollbar.å
    """
    # Process width and height for HTML
    width_style = f"width: {width}px;" if width is not None else "width: 100%;"
    height_style = f"height: {height}px;" if height is not None else "height: 500px;"

    # Set scrolling attribute
    scroll_attr = "yes" if scrolling else "no"

    # Check if data is a URL
    if isinstance(data, str) and (
        data.startswith("http://")
        or data.startswith("https://")
        or data.startswith("//")
    ):
        # For URLs, use HTML directly
        pdf_url = data
    else:
        # For local files or raw data, process and store in media file manager
        coordinates = st._main._get_delta_path_str()

        # Convert data to appropriate format
        data_or_filename: Union[bytes, str]
        if isinstance(data, (str, bytes)):
            # Pass strings and bytes through unchanged
            data_or_filename = data
        elif isinstance(data, Path):
            data_or_filename = str(data)
        elif isinstance(data, io.BytesIO):
            data.seek(0)
            data_or_filename = data.getvalue()
        elif isinstance(data, (io.RawIOBase, io.BufferedReader)):
            data.seek(0)
            read_data = data.read()
            if read_data is None:
                return None
            else:
                data_or_filename = read_data
        else:
            raise RuntimeError(f"Invalid PDF data format: {type(data)}")

        # Add to media file manager
        from streamlit.runtime import Runtime

        runtime = Runtime.instance()
        pdf_url = runtime.media_file_mgr.add(
            data_or_filename, "application/pdf", coordinates
        )

    html_content = f"""
    <iframe
        src="{pdf_url}"
        style="{width_style} {height_style}"
        scrolling="{scroll_attr}"
        type="application/pdf"
        frameborder="0"
    ></iframe>
    """

    # Display the PDF using st.html without height parameter
    st.markdown(html_content, unsafe_allow_html=True)


def example():
    """Example usage of the PDF viewer component."""
    pdf_viewer(
        "https://pdfobject.com/pdf/sample.pdf",
    )


__title__ = "PDF Viewer"
__desc__ = (
    "Display PDF documents from URLs or local files using native browser rendering."
)
__icon__ = "📄"
__examples__ = [example]
__author__ = "Lukas Masuch"
__playground__ = True
