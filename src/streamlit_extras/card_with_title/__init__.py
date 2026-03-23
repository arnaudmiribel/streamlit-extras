"""card_with_title — a permanently-expanded expander-style card with an optional header image."""

from __future__ import annotations

import html
import uuid
from contextlib import contextmanager
from typing import TYPE_CHECKING

import streamlit as st

from streamlit_extras import extra

if TYPE_CHECKING:
    from collections.abc import Generator

__version__ = "0.1.0"
__title__ = "Card with Title"
__desc__ = (
    "A card container that looks and feels exactly like ``st.expander`` "
    "but is permanently open — no collapse toggle. Optionally renders a "
    "header image above the title for a richer ``st.card`` prototype."
)
__icon__ = "\U0001f0cf"
__author__ = "Arnaud Miribel"
__streamlit_min_version__ = "1.37.0"


@extra
@contextmanager
def card_with_title(
    label: str,
    *,
    icon: str | None = None,
    image: str | None = None,
    max_image_height: int = 200,
    height: int | None = None,
    key: str | None = None,
) -> Generator[None, None, None]:
    """A permanently-expanded card container styled exactly like ``st.expander``.

    Works as a context manager — anything rendered inside the ``with`` block
    appears in the card body. Optionally accepts a header image URL to render a
    banner above the title, giving you a lightweight ``st.card`` prototype.

    The card is a real ``st.expander`` locked open via CSS and JS scoped to its
    unique ``st-key-*`` container class, so it inherits all native theming
    automatically.

    Args:
        label: Title text shown in the card header (same as ``st.expander``).
        icon: Optional emoji or Material icon shortcode, forwarded straight to
            ``st.expander``'s ``icon`` parameter.
        image: Optional URL of a banner image rendered inside the card, flush
            at the bottom.
        max_image_height: Maximum pixel height of the banner image. Defaults
            to ``200``.
        height: Optional fixed height in pixels for the card body. When set,
            the body scrolls if content overflows. Defaults to ``None``.
        key: Optional stable key for the container. A random UUID is used if
            omitted.

    Yields:
        Nothing — write Streamlit elements inside the ``with`` block as usual.

    Example:
        >>> with card_with_title("My card", icon="\U0001f4e6"):
        ...     st.write("Hello from inside the card!")
    """
    container_key = key or f"card-{uuid.uuid4().hex[:8]}"
    css_scope = f".st-key-{container_key}"

    height_css = (
        f'{css_scope} [data-testid="stExpanderDetails"] {{height: {height}px !important; overflow-y: auto !important;}}'
        if height is not None
        else ""
    )

    # Only stable selectors here:
    #   - st-key-{key}           our scoped hook
    #   - data-testid="..."      Streamlit's stable public API
    #   - .stExpander            friendly semantic class
    # No hash-based emotion-cache classes.
    st.html(f"""
<style>
  /* Disable click/hover cursor on summary */
  {css_scope} .stExpander summary {{
    pointer-events: none !important;
    cursor: default !important;
    user-select: none !important;
  }}
  /* Freeze opacity on all summary children to kill the hover fade.
     We target via data-testid and tag names only — no hash classes. */
  {css_scope} .stExpander summary [data-testid="stExpanderIcon"],
  {css_scope} .stExpander summary [data-testid="stExpanderIcon"] * {{
    opacity: 1 !important;
    transition: none !important;
  }}
  /* Zero the expander body padding so the bottom image sits flush */
  {css_scope} [data-testid="stExpanderDetails"] {{
    padding-top: 0.75rem !important;
    padding-bottom: 0 !important;
  }}
  {height_css}
</style>
<script>
(function() {{
  var KEY = "{container_key}";
  var HAS_ICON = {"true" if icon else "false"};

  function patch() {{
    var container = document.querySelector(".st-key-" + KEY);
    if (!container) return false;
    var summary = container.querySelector(".stExpander summary");
    if (!summary) return false;

    // The expander icon slot contains a [data-testid="stIconMaterial"] span.
    // When no user icon is set, its text is the chevron glyph name
    // ("keyboard_arrow_down" / "keyboard_arrow_right").
    // When a user icon IS set, it contains the icon value instead.
    // Strategy:
    //   - No icon: remove the entire icon slot so the label is flush-left.
    //   - With icon: remove only the chevron sibling, keep the user icon.
    // We identify the chevron by its known Material icon glyph names.
    var iconSlot = summary.querySelector("[data-testid=\"stExpanderIcon\"]");
    if (iconSlot) {{
      if (!HAS_ICON) {{
        iconSlot.remove();
      }} else {{
        var mat = iconSlot.querySelector("[data-testid=\"stIconMaterial\"]");
        if (mat) {{
          var t = mat.textContent.trim();
          if (t === "keyboard_arrow_down" || t === "keyboard_arrow_right") {{
            mat.remove();
          }}
        }}
      }}
    }}
    return true;
  }}

  if (!patch()) {{
    var id = setInterval(function() {{
      if (patch()) clearInterval(id);
    }}, 30);
    setTimeout(function() {{ clearInterval(id); }}, 3000);
  }}
}})();
</script>
""")

    with st.container(key=container_key):
        with st.expander(label=label, expanded=True, icon=icon or None):
            yield
            if image:
                image_safe = html.escape(image)
                st.html(
                    f"<img src='{image_safe}' alt='' style='"
                    f"display:block;"
                    f"width:calc(100% + 2rem);"
                    f"margin:0 -1rem -1rem -1rem;"
                    f"object-fit:cover;"
                    f"max-height:{max_image_height}px;"
                    f"border-radius:0 0 0.5rem 0.5rem;"
                    f"' />"
                )


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------


def example_basic() -> None:
    """A simple card with a title and icon."""
    with card_with_title("Revenue Summary", icon="\U0001f4b0", key="card_revenue"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", "$128,400", "+12%")
        col2.metric("Avg. Order", "$340", "-3%")
        col3.metric("Customers", "381", "+8%")
        st.caption("All figures are for the current quarter.")


def example_image_cards() -> None:
    """Two image cards side by side."""
    col1, col2 = st.columns(2)

    with col1:
        with card_with_title(
            "Mountain Retreat",
            icon="\U0001f3d4\ufe0f",
            image="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
            max_image_height=160,
            key="card_mountain",
        ):
            st.write("**Location:** Swiss Alps, Switzerland")
            st.write("**Rating:** \u2b50\u2b50\u2b50\u2b50\u2b50")
            st.button("Book Now", key="book_mountain")

    with col2:
        with card_with_title(
            "Beach Getaway",
            icon="\U0001f3d6\ufe0f",
            image="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
            max_image_height=160,
            key="card_beach",
        ):
            st.write("**Location:** Maldives")
            st.write("**Rating:** \u2b50\u2b50\u2b50\u2b50")
            st.button("Book Now", key="book_beach")


def example_label_and_image_only() -> None:
    """Three cards with only a label and image — no body content."""
    col1, col2, col3 = st.columns(3)

    with col1:
        with card_with_title(
            "Alps",
            image="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
            max_image_height=140,
            key="card_alps",
        ):
            pass

    with col2:
        with card_with_title(
            "Maldives",
            image="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
            max_image_height=140,
            key="card_maldives",
        ):
            pass

    with col3:
        with card_with_title(
            "Sahara",
            image="https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80",
            max_image_height=140,
            key="card_sahara",
        ):
            pass


__examples__ = [example_basic, example_image_cards, example_label_and_image_only]
