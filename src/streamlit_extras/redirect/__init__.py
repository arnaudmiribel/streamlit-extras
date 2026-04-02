"""Redirect to external URLs programmatically.

A Streamlit extra that enables programmatic redirection to external URLs,
useful for OAuth flows, conditional navigation, and user routing.
"""

from __future__ import annotations

import html
from datetime import date
from typing import Literal

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra

_REDIRECT_COMPONENT = st.components.v2.component(
    name="streamlit_extras.redirect",
    html="<div aria-hidden='true'></div>",
    js="""
    const processedUrls = new WeakMap();

    export default function (component) {
        const { data, parentElement } = component;

        const url = data?.url ?? "";
        const target = data?.target ?? "_self";
        const replaceHistory = data?.replace_history ?? false;
        const requestId = data?.request_id ?? 0;

        // Skip if no URL or already processed this request
        if (!url || processedUrls.get(parentElement) === requestId) {
            return () => {};
        }

        processedUrls.set(parentElement, requestId);

        try {
            if (target === "_blank") {
                // Open in new tab
                window.open(url, "_blank", "noopener,noreferrer");
            } else {
                // Redirect in same tab - use top-level window to escape iframe
                const targetWindow = window.top || window.parent || window;
                if (replaceHistory) {
                    // Replace current history entry (useful for OAuth flows)
                    targetWindow.location.replace(url);
                } else {
                    // Normal navigation (adds to history)
                    targetWindow.location.href = url;
                }
            }
        } catch (error) {
            // Fallback if top/parent access is blocked by same-origin policy
            console.warn("Redirect failed, trying fallback:", error);
            if (target === "_blank") {
                window.open(url, "_blank", "noopener,noreferrer");
            } else if (replaceHistory) {
                window.location.replace(url);
            } else {
                window.location.href = url;
            }
        }

        return () => {};
    }
    """,
)


def _validate_url(url: str) -> str:
    """Validate and sanitize the URL to prevent injection attacks.

    Args:
        url: The URL to validate.

    Returns:
        The validated URL.

    Raises:
        ValueError: If the URL is invalid or uses a disallowed scheme.
    """
    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty")

    # Escape HTML entities to prevent XSS in the URL
    url = html.unescape(url)

    # Allow only safe URL schemes
    url_lower = url.lower()
    if url_lower.startswith(("javascript:", "data:")):
        raise ValueError("URLs with 'javascript:' or 'data:' schemes are not allowed for security reasons.")

    # Must be http://, https://, or relative path
    if not (url_lower.startswith(("http://", "https://")) or url.startswith("/")):
        raise ValueError(
            "URL must start with 'http://', 'https://', or '/' (relative path). "
            f"Got: {url[:50]}{'...' if len(url) > 50 else ''}"
        )

    return url


@extra
def redirect(
    url: str,
    *,
    target: Literal["_self", "_blank"] = "_self",
    replace_history: bool = False,
) -> None:
    """Redirect the browser to a specified URL.

    This component triggers a browser redirect to an external or internal URL.
    It's useful for OAuth flows, conditional navigation, or routing users
    based on application state.

    Args:
        url: The URL to redirect to. Must use http://, https://, or be a
            relative path starting with /.
        target: Where to open the URL. Use "_self" (default) to redirect the
            current tab, or "_blank" to open in a new tab.
        replace_history: If True, replaces the current browser history entry
            instead of adding a new one. Useful for OAuth flows where you
            don't want users to navigate back to an incomplete auth state.
            Only applies when target is "_self". Default is False.

    Example:

        ```python
        if st.button("Go to GitHub"):
            redirect("https://github.com/streamlit/streamlit")
        ```

    Note:
        - For same-tab redirects (_self), the Streamlit app will be replaced
        - For new-tab redirects (_blank), popup blockers may prevent the action
        - URLs are validated to prevent javascript: and other unsafe schemes
        - A ValueError is raised if the URL is empty or uses an unsafe scheme
    """
    validated_url = _validate_url(url)

    # Use st._event container to avoid adding any visual space to the UI
    with st._event:
        _REDIRECT_COMPONENT(
            data={
                "url": validated_url,
                "target": target,
                "replace_history": replace_history,
                "request_id": 1,
            },
            width="stretch",
            height=0,
        )


def example_same_tab() -> None:
    """Example: Redirect in the same tab."""
    st.write("Click the button to redirect to the Streamlit GitHub repository.")

    if st.button("Go to Streamlit GitHub", key="redirect_same_tab"):
        redirect("https://github.com/streamlit/streamlit")


def example_new_tab() -> None:
    """Example: Open URL in a new tab."""
    st.write("Click the button to open the Streamlit docs in a new tab.")

    if st.button("Open Streamlit Docs", key="redirect_new_tab"):
        redirect("https://docs.streamlit.io", target="_blank")


def example_oauth_flow() -> None:
    """Example: OAuth-style redirect that replaces history."""
    st.write(
        "This demonstrates an OAuth-style redirect that replaces the browser history, "
        "preventing users from navigating back to an incomplete auth state."
    )

    if st.button("Simulate OAuth Redirect", key="redirect_oauth"):
        # In a real app, this would redirect to an OAuth provider
        redirect("https://example.com/oauth/authorize", replace_history=True)


def example_conditional() -> None:
    """Example: Conditional redirect based on user input."""
    st.write("Enter a search query and press Enter to search on Google.")

    query = st.text_input("Search query", key="search_query")
    if query:
        # URL-encode the query for safe use in the URL
        from urllib.parse import quote

        search_url = f"https://www.google.com/search?q={quote(query)}"
        if st.button("Search", key="redirect_search"):
            redirect(search_url, target="_blank")


__title__ = "Redirect"
__desc__ = "Programmatically redirect users to external or internal URLs."
__icon__ = "🔀"
__examples__ = [example_same_tab, example_new_tab, example_oauth_flow, example_conditional]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 3, 24)
