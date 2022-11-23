import textwrap

import streamlit as st
from markdownlit import mdlit

from .. import extra

mdlit = extra(mdlit)


def mdlit_example(code: str) -> None:
    left, right = st.columns((2, 25))
    with left:
        mdlit("[gray]<small style='float:right'>In:</small>[/gray]")
    right.code(
        f"""mdlit("{code}")""",
        "python",
    )
    left, right = st.columns((2, 25))
    with left:
        mdlit("[gray]<small style='float:right'>Out:</small>[/gray]")
    with right:
        mdlit(code)


def example_link_and_colors():
    mdlit(
        """Tired from [default links](https://extras.streamlit.app)?
    Me too! Discover Markdownlit's `@()` operator. Just insert a link and it
    will figure a nice icon and label for you!
    Example: @(https://extras.streamlit.app)... better, right? You can
    also @(🍐)(manually set the label if you want)(https://extras.streamlit.app)
    btw, and play with a [red]beautiful[/red] [blue]set[/blue] [orange]of[/orange]
    [violet]colors[/violet]. Another perk is those beautiful arrows -> <-
    """
    )


def example_collapsible_content():
    mdlit(
        textwrap.dedent(
            """
    ??? Bonus
        @(🎁)(A very insightful tutorial)(https://www.youtube.com/watch?v=dQw4w9WgXcQ)
    """
        )
    )


__func__ = mdlit
__title__ = "Markdownlit"
__desc__ = """markdownlit is a Markdown command in Python which puts together a few additional capabilities foreseen to be useful in the context of @(Streamlit)(streamlit.io) apps. It is built as an extension to the great @(https://github.com/Python-Markdown/markdown) project. You can use markdownlit along with `st.markdown()`!

Here are the features of markdownlit:

1. **Magic links** like @(🍐)(Pear)(https://www.youtube.com/watch?v=dQw4w9WgXcQ), @(https://youtube.com) @(twitter.com/arnaudmiribel), @(github.com/arnaudmiribel/streamlit-extras)
2. **Colored text.** Includes [red]red[/red], [green]green[/green], [blue]blue[/blue], [orange]orange[/orange] and [violet]violet[/violet].
3. ??? "**Collapsible content.** See this > toggle you're using right now!"
       Funny, right!
4. **Beautiful arrows.** Arrows - > are automatically translated to →
5. **Beautiful dashes.** Double dashes - - are automatically translated to —
"""
__icon__ = "〽️"
__examples__ = [
    example_link_and_colors,
    example_collapsible_content,
]
__author__ = "Arnaud Miribel"
__github_repo__ = "arnaudmiribel/markdownlit"
__pypi_name__ = "markdownlit"
__package_name__ = "markdownlit"
__experimental_playground__ = True
