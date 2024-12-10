from htbuilder import span, styles
from htbuilder.units import px
from streamlit import streamlit as st
from streamlit.components.v1 import html

from .. import extra


@extra
def star_rating(rating: float, color: str = "#FFD700"):
    """
    Renders a read-only star rating component using htbuilder for Streamlit.

    Args:
        rating (float): A number in the range [0, 5] representing the rating to be displayed. It can include half values like 2.5, and will be rounded to the nearest half-integer.
        color (str, optional): The color of the stars. Defaults to gold ("#FFD700").
    """

    # Sanitize the rating to ensure it stays within [0, 5]
    assert 0.0 <= rating <= 5.0, "Rating must be in the range [0, 5]"

    # Calculate the number of full stars, half stars, and empty stars
    full_stars = int(rating)
    half_star = 1 if rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    def render_star(star_type="full"):
        # Common style for stars
        star_style = styles(
            color=color if star_type != "empty" else "lightgrey",
            font_size=px(24),
            border_radius=px(5),
            # padding=px(2),
            margin_right=px(2),
            cursor="default",
            user_select="none",
        )

        # Star HTML
        star_html = span(style=star_style)("★")

        # Apply half-star effect
        if star_type == "half":
            half_star_style = styles(
                position="absolute",
                left=px(0),
                width=px(12),
                overflow="hidden",
                color=color,
                user_select="none",
            )
            star_html = span(
                style=styles(
                    color="lightgrey",
                    font_size=px(24),
                    position="relative",
                    user_select="none",
                )
            )("★", span(style=half_star_style)("★"))

        return star_html

    # Create HTML content
    stars_html = (
        [render_star("full") for _ in range(full_stars)]
        + [render_star("half") for _ in range(half_star)]
        + [render_star("empty") for _ in range(empty_stars)]
    )

    html_content = "".join(map(str, stars_html))

    html(html_content, height=47, width=150)


def example():
    st.text("10/10 would watching")
    star_rating(5)


__title__ = "Read-only Star Rating Component"
__desc__ = "A read-only Star rating using htbuilder for Streamlit."
__icon__ = "⭐"
__examples__ = [example]
__author__ = "Gabriel Vidal"
__experimental_playground__ = True
