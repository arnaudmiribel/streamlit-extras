from datetime import date

import streamlit as st

from .. import extra


@extra
def star_rating(rating: float, color: str = "#FFD700") -> None:
    """
    Renders a read-only star rating component for Streamlit.

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

    def render_star(star_type: str = "full") -> str:
        star_color = color if star_type != "empty" else "lightgrey"
        base_style = (
            f"color:{star_color};font-size:24px;border-radius:5px;margin-right:2px;cursor:default;user-select:none;"
        )

        if star_type == "half":
            # Half star with overlay effect
            return f'<span style="color:lightgrey;font-size:24px;position:relative;user-select:none;">★<span style="position:absolute;left:0;width:12px;overflow:hidden;color:{color};user-select:none;">★</span></span>'
        return f'<span style="{base_style}">★</span>'

    # Create HTML content
    stars_html = (
        [render_star("full") for _ in range(full_stars)]
        + [render_star("half") for _ in range(half_star)]
        + [render_star("empty") for _ in range(empty_stars)]
    )

    html_content = "".join(stars_html)

    st.html(html_content, width="content")


def example() -> None:
    st.text("10/10 would watching")
    star_rating(5)


__title__ = "Read-only Star Rating Component"
__desc__ = "A read-only Star rating component for Streamlit."
__icon__ = "⭐"
__examples__ = [example]
__author__ = "Gabriel Vidal"
__created_at__ = date(2024, 10, 5)
__experimental_playground__ = True
