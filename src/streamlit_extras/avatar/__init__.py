"""Display a circular avatar image with optional label and caption.

A Streamlit Custom Component v2 (CCv2) that renders a circular avatar image,
optionally with a label and caption displayed to the right. Supports click
interactions for profile-like UI patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal
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

_AVATAR_COMPONENT = st.components.v2.component(
    name="streamlit_extras.avatar",
    html="""
    <style>
        :host {
            overflow: hidden;
        }
        .avatar-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.25rem;
            border-radius: 0.5rem;
            box-sizing: border-box;
            width: 100%;
            max-width: 100%;
            overflow: hidden;
        }
        .avatar-container.clickable {
            cursor: pointer;
        }
        .avatar-image {
            border-radius: 50%;
            object-fit: cover;
            flex-shrink: 0;
            display: block;
            margin: 0;
            padding: 0;
        }
        .avatar-text {
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 0;
            overflow: hidden;
            flex: 1;
        }
        .avatar-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--st-text-color, inherit);
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .avatar-caption {
            font-size: 0.75rem;
            color: var(--st-secondary-text-color, #6b7280);
            line-height: 1.3;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    </style>
    <div class="avatar-container" id="avatar-root"></div>
    """,
    js="""
    // Resolve media URLs to absolute URLs
    function resolveMediaUrl(url) {
        if (!url) return url;

        // Already absolute URL
        if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) {
            return url;
        }

        // Handle /media/ paths
        if (url.startsWith("/media/") || url.startsWith("media/")) {
            const normalizedUrl = url.startsWith("/") ? url : "/" + url;

            // Try to get base URL from Streamlit config or window location
            let baseUrl = "";
            if (window.__streamlit?.DOWNLOAD_ASSETS_BASE_URL) {
                baseUrl = window.__streamlit.DOWNLOAD_ASSETS_BASE_URL;
            } else if (window.location) {
                baseUrl = window.location.origin + window.location.pathname;
            }

            if (baseUrl) {
                try {
                    const parsed = new URL(baseUrl);
                    let basePath = parsed.pathname;
                    if (!basePath.endsWith("/")) {
                        const lastSlash = basePath.lastIndexOf("/");
                        basePath = lastSlash > 0 ? basePath.substring(0, lastSlash) : "";
                    } else {
                        basePath = basePath.slice(0, -1);
                    }
                    return parsed.origin + (basePath + normalizedUrl).replace(/\\/+/g, "/");
                } catch (e) {
                    return url;
                }
            }
        }

        return url;
    }

    export default function(component) {
        const { data, setStateValue, parentElement } = component;

        const imageUrl = data?.image_url ?? "";
        const height = data?.height ?? 48;
        const label = data?.label ?? "";
        const caption = data?.caption ?? "";
        const clickable = data?.clickable ?? false;

        const container = parentElement.querySelector("#avatar-root");
        if (!container) return () => {};

        // Clear previous content
        container.innerHTML = "";

        // Set clickable class and accessibility attributes
        if (clickable) {
            container.classList.add("clickable");
            container.setAttribute("role", "button");
            container.setAttribute("tabindex", "0");
            container.setAttribute("aria-label", label || "Avatar");
        } else {
            container.classList.remove("clickable");
            container.removeAttribute("role");
            container.removeAttribute("tabindex");
            container.removeAttribute("aria-label");
        }

        // Create image element
        const img = document.createElement("img");
        img.className = "avatar-image";
        img.src = resolveMediaUrl(imageUrl);
        img.alt = label || "Avatar";
        img.width = height;
        img.height = height;
        img.style.width = height + "px";
        img.style.height = height + "px";
        container.appendChild(img);

        // Create text container if label or caption exists
        if (label || caption) {
            const textDiv = document.createElement("div");
            textDiv.className = "avatar-text";

            if (label) {
                const labelDiv = document.createElement("div");
                labelDiv.className = "avatar-label";
                labelDiv.textContent = label;
                labelDiv.title = label;
                textDiv.appendChild(labelDiv);
            }

            if (caption) {
                const captionDiv = document.createElement("div");
                captionDiv.className = "avatar-caption";
                captionDiv.textContent = caption;
                captionDiv.title = caption;
                textDiv.appendChild(captionDiv);
            }

            container.appendChild(textDiv);
        }

        // Handle click - increment counter for each click
        const handleClick = () => {
            if (clickable) {
                const currentCount = component.getStateValue("click_count") ?? 0;
                setStateValue("click_count", currentCount + 1);
            }
        };

        // Handle keyboard activation (Enter/Space)
        const handleKeyDown = (e) => {
            if (clickable && (e.key === "Enter" || e.key === " ")) {
                e.preventDefault();
                handleClick();
            }
        };

        container.addEventListener("click", handleClick);
        container.addEventListener("keydown", handleKeyDown);

        return () => {
            container.removeEventListener("click", handleClick);
            container.removeEventListener("keydown", handleKeyDown);
        };
    }
    """,
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
def avatar(
    image: ImageLike,
    *,
    label: str | None = None,
    caption: str | None = None,
    height: int = 48,
    on_click: Literal["ignore", "rerun"] | Callable[[], None] = "ignore",
    key: str | None = None,
) -> bool:
    """Display a circular avatar image with optional label and caption.

    This component renders a circular avatar image, commonly used for user profiles,
    contact lists, or any UI that needs to display a person or entity visually.
    Optionally displays a label and caption to the right of the image.

    Args:
        image: The image to display. Supports URLs (str), file paths (str or Path),
            PIL images, numpy arrays, or raw bytes/BytesIO.
        label: Optional primary text displayed to the right of the avatar.
            Typically used for names or titles.
        caption: Optional secondary text displayed below the label.
            Typically used for roles, status, or descriptions.
        height: Avatar height (and width) in pixels. Defaults to 48.
        on_click: Click behavior. "ignore" (default) disables click interactions.
            "rerun" triggers an app rerun when clicked. Pass a callable to execute
            a custom callback when clicked.
        key: Unique key for this component instance. Required when using multiple
            avatars with the same parameters.

    Returns:
        True if the avatar was clicked on this run (when on_click != "ignore"),
        False otherwise. Always returns False when on_click is "ignore".

    Raises:
        StreamlitAPIException: If height is less than 1 or on_click has an
            invalid value.

    Example:
        Simple avatar:

        ```python
        avatar("https://avatars.githubusercontent.com/u/12345")
        ```

        Avatar with label and caption:

        ```python
        avatar(
            "https://avatars.githubusercontent.com/u/12345",
            label="John Doe",
            caption="Software Engineer",
        )
        ```

        Clickable avatar:

        ```python
        if avatar(
            "profile.jpg",
            label="Jane Smith",
            on_click="rerun",
        ):
            st.write("Profile clicked!")
        ```
    """
    # Validate height
    if height < 1:
        raise StreamlitAPIException(f"Avatar height must be at least 1 pixel, got {height}.")

    # Validate on_click
    if not callable(on_click) and on_click not in ("ignore", "rerun"):
        raise StreamlitAPIException(f"on_click must be 'ignore', 'rerun', or a callable, got {on_click!r}.")

    # Convert image to URL
    image_url = _convert_image_to_url(image)

    # Determine if clickable
    clickable = on_click != "ignore"

    # Prepare callback if needed
    callback: Callable[[], None] | None = None
    if callable(on_click):
        callback = on_click
    elif on_click == "rerun":
        callback = lambda: None  # noqa: E731 - Just triggers rerun via component

    # Calculate component height based on avatar height
    # Avatar height + padding (0.25rem * 2 = 0.5rem ≈ 8px) + small buffer
    component_height = height + 10

    # Build component kwargs - only include click state when clickable
    component_kwargs: dict[str, Any] = {
        "key": key,
        "data": {
            "image_url": image_url,
            "height": height,
            "label": label or "",
            "caption": caption or "",
            "clickable": clickable,
        },
        "height": component_height,
    }

    if clickable:
        component_kwargs["default"] = {"click_count": 0}
        component_kwargs["on_click_count_change"] = callback

    # Render component
    result = _AVATAR_COMPONENT(**component_kwargs)

    # Detect if clicked this run by checking if click_count increased
    if clickable:
        click_count = result.click_count if result.click_count is not None else 0
        # Store previous click count in session state to detect new clicks
        state_key = f"_avatar_click_count_{key or id(result)}"
        prev_count = st.session_state.get(state_key, 0)
        st.session_state[state_key] = click_count
        return click_count > prev_count
    return False


def example() -> None:
    """Example usage of the avatar component."""
    st.subheader("Basic avatars")

    col1, col2, col3 = st.columns(3)

    with col1:
        avatar(
            "https://avatars.githubusercontent.com/u/1673013?v=4",
            label="Adrien Treuille",
            caption="Co-founder",
        )

    with col2:
        avatar(
            "https://avatars.githubusercontent.com/u/690814?v=4",
            label="Thiago Teixeira",
            caption="Co-founder",
        )

    with col3:
        avatar(
            "https://avatars.githubusercontent.com/u/47222480?v=4",
            label="Amanda Kelly",
            caption="Co-founder",
        )

    st.subheader("Different heights")

    col1, col2, col3 = st.columns(3)

    with col1:
        avatar(
            "https://avatars.githubusercontent.com/u/1673013?v=4",
            height=32,
            label="Small (32px)",
        )

    with col2:
        avatar(
            "https://avatars.githubusercontent.com/u/1673013?v=4",
            height=48,
            label="Medium (48px)",
        )

    with col3:
        avatar(
            "https://avatars.githubusercontent.com/u/1673013?v=4",
            height=64,
            label="Large (64px)",
        )

    st.subheader("Clickable avatar")

    if avatar(
        "https://avatars.githubusercontent.com/u/1673013?v=4",
        label="Click me!",
        caption="I'm interactive",
        on_click="rerun",
        key="clickable_avatar",
    ):
        st.toast("Avatar clicked!")

    st.subheader("Avatar only (no text)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avatar("https://avatars.githubusercontent.com/u/1673013?v=4", height=40)
    with col2:
        avatar("https://avatars.githubusercontent.com/u/690814?v=4", height=40)
    with col3:
        avatar("https://avatars.githubusercontent.com/u/47222480?v=4", height=40)
    with col4:
        avatar("https://avatars.githubusercontent.com/u/12345", height=40)


__title__ = "Avatar"
__desc__ = "Display a circular avatar image with optional label and caption."
__icon__ = "👤"
__examples__ = [example]
__author__ = "Lukas Masuch"
__streamlit_min_version__ = "1.46.0"
