"""Scroll to elements programmatically by their key.

A Streamlit extra that enables programmatic scrolling to any element
that has a `key` parameter set. Useful for navigation within long pages,
directing user attention, and form workflows.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Literal

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra

_SCROLL_COMPONENT = st.components.v2.component(
    name="streamlit_extras.scroll_to_element",
    html="<div aria-hidden='true'></div>",
    js="""
    const processedRequests = new WeakMap();

    export default function (component) {
        const { data, parentElement } = component;

        const className = data?.class_name ?? "";
        const scrollMode = data?.scroll_mode ?? "smooth";
        const alignment = data?.alignment ?? "center";
        const requestId = data?.request_id ?? 0;

        // Skip if no class name or already processed this request
        if (!className || processedRequests.get(parentElement) === requestId) {
            return () => {};
        }

        processedRequests.set(parentElement, requestId);

        // Only "auto" and "smooth" are valid for scrollIntoView behavior.
        // Map any other value (including "instant") to "auto" to avoid TypeError.
        const behavior = scrollMode === "smooth" ? "smooth" : "auto";

        const scrollOptions = {
            behavior: behavior,
            block: alignment,
            inline: "nearest"
        };

        // Helper to find and scroll to element in a document
        const findAndScroll = (doc) => {
            const element = doc.querySelector("." + CSS.escape(className));
            if (element) {
                element.scrollIntoView(scrollOptions);
                return true;
            }
            return false;
        };

        // Try window.parent first (Streamlit app's document when component is iframed)
        // This is the most common case and works on Community Cloud when the app is iframed
        try {
            if (window.parent && window.parent !== window && findAndScroll(window.parent.document)) {
                return () => {};
            }
        } catch (e) {
            // Cross-origin or sandbox restriction - continue to next option
        }

        // Try window.top (when Streamlit app is the top-level window)
        try {
            if (window.top && findAndScroll(window.top.document)) {
                return () => {};
            }
        } catch (e) {
            // Cross-origin or sandbox restriction - continue to fallback
        }

        // Final fallback: current document (unlikely to have the element, but try anyway)
        try {
            findAndScroll(document);
        } catch (e) {
            console.warn("Scroll to element: unexpected error while attempting to scroll in current document", e);
        }

        return () => {};
    }
    """,
)


def _key_to_class_name(key: str) -> str:
    """Convert a Streamlit element key to its CSS class name.

    Streamlit adds a class with the pattern `st-key-{sanitized_key}` to elements
    that have a key parameter set. This function replicates that sanitization.

    Args:
        key: The element key as passed to Streamlit widgets.

    Returns:
        The CSS class name that Streamlit assigns to the element.
    """
    # Replace non-alphanumeric characters (except - and _) with -
    class_name = re.sub(r"[^a-zA-Z0-9_-]", "-", key.strip())
    return f"st-key-{class_name}"


@extra
def scroll_to_element(
    key: str,
    *,
    scroll_mode: Literal["smooth", "instant", "auto"] = "smooth",
    alignment: Literal["start", "center", "end", "nearest"] = "center",
) -> None:
    """Scroll the page to an element with the specified key.

    This component scrolls the browser viewport to make a specific element
    visible. The target element must have been created with a `key` parameter
    (e.g., `st.text_input("Label", key="my_key")`).

    Args:
        key: The key of the target element to scroll to. The element must have
            been created with a `key` parameter.
        scroll_mode: The scroll behavior. "smooth" animates the scroll, "instant"
            jumps immediately, "auto" uses browser preference. Default is "smooth".
        alignment: Where to position the element in the viewport after scrolling.
            "start" aligns to the top, "center" centers it, "end" aligns to the
            bottom, "nearest" scrolls the minimum distance. Default is "center".

    Example:

        ```python
        st.text_input("Name", key="name_field")
        if st.button("Jump to name field"):
            scroll_to_element("name_field")
        ```

    Note:
        - The target element must have a `key` parameter set in its Streamlit call
        - If no element with the specified key exists, the scroll is silently ignored
        - Use conditionally (e.g., in button callbacks) to avoid scrolling on every rerun
    """
    if not key or not key.strip():
        return

    class_name = _key_to_class_name(key)

    # Use st._event container to avoid adding any visual space to the UI
    with st._event:
        _SCROLL_COMPONENT(
            data={
                "class_name": class_name,
                "scroll_mode": scroll_mode,
                "alignment": alignment,
                "request_id": 1,
            },
            width="stretch",
            height=0,
        )


def example_basic() -> None:
    """Example: Basic scroll navigation."""
    st.write("Click the buttons to scroll to different sections of the page.")

    # Navigation buttons at the top
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Go to Introduction", key="nav_intro"):
            scroll_to_element("intro_section")
    with col2:
        if st.button("Go to Name Input", key="nav_name"):
            scroll_to_element("name_input")
    with col3:
        if st.button("Go to Middle Section", key="nav_middle"):
            scroll_to_element("middle_section")
    with col4:
        if st.button("Go to Conclusion", key="nav_conclusion"):
            scroll_to_element("conclusion_section")

    # Create sections with keys using containers
    with st.container(key="intro_section"):
        st.header("Introduction")
        st.write(
            "This example demonstrates how to scroll to elements by their key. "
            "Click the buttons above to navigate between sections."
        )

    # Add some spacer content
    for i in range(10):
        st.write(f"Content block {i + 1}")

    with st.container(key="middle_section"):
        st.header("Middle Section")
        st.text_input("Enter your name", key="name_input")
        st.write("This is the middle of the page with a text input.")

    for i in range(10):
        st.write(f"More content {i + 1}")

    with st.container(key="conclusion_section"):
        st.header("Conclusion")
        st.write("You've reached the end of the page!")


def example_smooth_vs_instant() -> None:
    """Example: Compare smooth and instant scrolling."""
    st.write("Compare different scroll behaviors.")

    with st.container(key="scroll_target"):
        st.header("Target Element")
        st.info("This is the target element for scrolling.")

    for i in range(15):
        st.write(f"Spacer content line {i + 1}")

    st.subheader("Scroll Options")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Smooth scroll", key="smooth_btn"):
            scroll_to_element("scroll_target", scroll_mode="smooth")

    with col2:
        if st.button("Instant scroll", key="instant_btn"):
            scroll_to_element("scroll_target", scroll_mode="instant")

    with col3:
        if st.button("Align to top", key="center_btn"):
            scroll_to_element("scroll_target", alignment="start")


__title__ = "Scroll to Element"
__desc__ = "Programmatically scroll to any element by its key."
__icon__ = "📜"
__examples__ = [example_basic, example_smooth_vs_instant]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 3, 24)
