import itertools
import math
from typing import Dict, Tuple

import pandas as pd
import streamlit as st
from htbuilder import a, div, img, p, span, styles

from .. import extra


@st.experimental_memo
def _get_example_df_bis():
    return pd.DataFrame(
        {
            "image_url": {
                "0": "http://placekitten.com/114/123",
                "1": "http://placekitten.com/88/125",
                "2": "http://placekitten.com/115/123",
                "3": "http://placekitten.com/129/111",
                "4": "http://placekitten.com/100/121",
                "5": "http://placekitten.com/119/127",
            },
            "description": {
                "0": "American whole magazine truth stop whose. On traditional measure example sense peace. Would mouth relate own chair.\nTogether range line beyond. First policy daughter need kind miss.",
                "1": "Language ball floor meet usually board necessary. Natural sport music white.",
                "2": "Every manage political record word group food break. Picture suddenly drug rule bring determine some forward. Beyond chair recently and.",
                "3": "Per structure attorney author feeling job. Mean always beyond write. Employee toward like total now.\nSmall citizen class morning. Others kind company likely.",
                "4": "Security stock ball organization recognize civil. Pm her then nothing increase.",
                "5": "First degree response able state more. Couple part cup few. Beyond take however ball.\nSon break either president stage population boy. Everything affect American race.",
            },
            "name": {
                "0": "Susan Johnson",
                "1": "Shelby Cox",
                "2": "Megan Hall",
                "3": "Brandon Melton",
                "4": "Patricia Andrade",
                "5": "Anthony Terry",
            },
            "city": {
                "0": "📍 East Mollystad",
                "1": "📍 Port James",
                "2": "📍 Larryfurt",
                "3": "📍 Timothybury",
                "4": "📍 West Sarahland",
                "5": "📍 South Tylermouth",
            },
            "social": {
                "0": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>📟  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Kid Painting</span><span></span></a>',
                "1": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>‍🦋  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Plant Evening</span><span></span></a>',
                "2": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🤱  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Budget Situation</span><span></span></a>',
                "3": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🌺  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Common Increase</span><span></span></a>',
                "4": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🥬  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Expect Save</span><span></span></a>',
                "5": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🔘  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Score Middle</span><span></span></a>',
            },
            "other_link": {
                "0": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🚋  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Career Deal</span><span></span></a>',
                "1": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>‍🧮  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Notice Receive</span><span></span></a>',
                "2": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>‍🏀  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Dog Car</span><span></span></a>',
                "3": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>️🤟  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Service Government</span><span></span></a>',
                "4": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🪤  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Pick Too</span><span></span></a>',
                "5": '\n<style>\na:hover {\n    background-color: rgba(.7, .7, .7, .05);\n}\n</style>\n<a contenteditable="False" href="https://streamlit.io" rel="noopener noreferrer" style="color:inherit;text-decoration:inherit; height:auto!important" target="_blank"><span></span>🧔  <span style="border-bottom:0.05em solid rgba(55,53,47,0.25);font-weight:500;flex-shrink:0">Pattern Ago</span><span></span></a>',
            },
        }
    )


def _space(num_lines=1):
    for _ in range(num_lines):
        st.write("")


@st.experimental_memo
def _to_image(url: str):
    image = str(a(href=url, target="_blank")(img(_class="screenshot", src=url)))
    return image


_PALETTE = itertools.cycle(
    [
        "rgba(206, 205, 202, 0.5)",
        "rgba(221, 0, 129, 0.2)",
        "rgba(245, 93, 0, 0.2)",
        "rgba(0, 135, 107, 0.2)",
        "rgba(103, 36, 222, 0.2)",
        "rgba(140, 46, 0, 0.2)",
    ]
)


def _to_tag(label: str):
    color = next(_PALETTE)
    tag = str(
        span(
            style=styles(
                **{
                    "background-color": color,
                    "padding": "1px 6px",
                    "display": "inline",
                    "vertical-align": "middle",
                    "border-radius": "12px",
                    "font-size": "0.75em",
                    "font-weight": 400,
                }
            )
        )(label)
    )
    return tag


_CARD_CSS = """
<style>
    .card {
    margin-top: 0px;
    /* box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); */
    /* border-radius: 5px; /* 5px rounded corners */*/
    /* transition: 0.3s; */
    flex-basis: 0;
    flex-grow: 1;
    border-color: rgba(49, 51, 63, 0.2);
    border-radius: 12px;
    border-style: solid;
    border-width: 1px;
    }

    /* On mouse-over, add a deeper shadow
    .card:hover {
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }*/

    /* Add some padding inside the card container */
    .card-container {
    padding: 20px 16px;

    }

    /* Add rounded corners to the top left and the top right corner of the image */
    .card-img {
    border-radius: 12px 12px 0 0;
    height: 150px;
    object-fit: cover;
    }
</style>
"""


@st.experimental_memo
def _card_builder(
    df_element: pd.DataFrame,
    columns: dict,
) -> str:

    # Validate card types
    assert isinstance(columns, dict), NotImplementedError(
        "For now, column types must be explicitly given."
    )

    # Check there's one image only
    image_type_columns = [c for c in columns if columns[c]["type"] == "image"]
    assert (
        len([c for c in columns if columns[c]["type"] == "image"]) == 1
    ), "There must be exactly one type 'image'."
    image_type_column = image_type_columns[0]

    # Check there's one title only
    title_type_columns = [c for c in columns if columns[c]["type"] == "title"]
    assert (
        len([c for c in columns if columns[c]["type"] == "title"]) == 1
    ), "There must be exactly one type 'title'."
    title_type_column = title_type_columns[0]

    tag_type_columns = [c for c in columns if columns[c]["type"] == "tag"]
    text_type_columns = [c for c in columns if columns[c]["type"] == "text"]
    html_type_columns = [c for c in columns if columns[c]["type"] == "html"]

    # Create card
    card = div(_class="card")(
        img(
            src=getattr(df_element, image_type_column),
            _class="card-img",
            style=styles(width="100%"),
        ),
        div(_class="card-container")(
            # Title
            p(
                getattr(df_element, title_type_column),
                style=styles(
                    font_size="22px",
                    margin_top="5px",
                    margin_bottom="0px",
                    font_weight="bold",
                ),
            ),
            # Tags
            "&nbsp;&nbsp;".join(
                [_to_tag(getattr(df_element, column)) for column in tag_type_columns]
            ),
            p(),
            # Text
            # Look at https://stackoverflow.com/questions/55351096/ellipsis-three-dots-expand-and-collapse-the-text
            # To add '...' logic.
            "\n".join(
                [str(p(getattr(df_element, column))) for column in text_type_columns]
            ),
            # Links
            "<br>".join([getattr(df_element, column) for column in html_type_columns]),
        ),
    )
    return str(card) + _CARD_CSS


@extra
@st.experimental_memo
def gallery(df: pd.DataFrame, columns: Dict, spec: Tuple = (None, 3)):
    """Displays a dataframe in a gallery view, with each row being shown as a card.
    Specify how which column should appear using the 'columns' kwarg.

    Example call:
        gallery(
            example_df,
            columns={
                "image_url": {"type": "image"},
                "name": {"type": "title"},
                "city": {"type": "tag"},
                "description": {"type": "text"},
                "social": {"type": "html"},
                "other_link": {"type": "html"},
            },
            spec=(None, 3),  # 3 columns!
        )

    Args:
        df (pd.DataFrame): Original dataframe
        columns (Dict): Columns that should be displayed and their types
        spec (Tuple, optional): Number of rows/columns in the gallery.
                                Defaults to (None, 3), meaning 3 columns and as
                                many rows as necessary.

    """

    if df.empty:
        st.caption("Empty gallery.")

    assert isinstance(columns, dict), NotImplementedError(
        "For now, column types must be explicitly given."
    )

    num_cards = len(df)

    # Spec validation
    num_rows, num_cols = spec
    assert any(spec), "You must give a valid spec. Examples: (1, 3) or (None, 4)"
    if num_rows is None:
        num_rows = math.ceil(num_cards / num_cols)
    assert num_cols is not None

    card_index = 0

    for _ in range(num_rows):
        for col, df_element in itertools.zip_longest(
            st.columns(num_cols),
            list(df.iloc[card_index : card_index + num_cols].itertuples()),
        ):
            if df_element:
                with col:
                    card_html = _card_builder(df_element, columns)
                    st.write(card_html, unsafe_allow_html=True)
            else:
                col.write("")  # Ensure 3 columns even when less apps

        card_index += num_cols
        _space(1)


def example():
    st.caption("Dataframe")
    example_df = _get_example_df_bis()
    st.dataframe(example_df)

    st.caption("Gallery view")
    gallery(
        example_df,
        columns={
            "image_url": {"type": "image"},
            "name": {"type": "title"},
            "city": {"type": "tag"},
            "description": {"type": "text"},
            "social": {"type": "html"},
            "other_link": {"type": "html"},
        },
        spec=(None, 3),  # 3 columns!
    )


__title__ = "Gallery"
__desc__ = "Make a gallery from a dataframe"
__icon__ = "🃏"
__examples__ = [example]
__author__ = "Arnaud Miribel"
