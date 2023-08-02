from streamlit_qs import (
    add_qs_callback,
    blacklist_key,
    checkbox_qs,
    clear_qs_callback,
    from_query_args,
    from_query_args_index,
    make_query_string,
    multiselect_qs,
    number_input_qs,
    radio_qs,
    selectbox_qs,
    text_area_qs,
    text_input_qs,
    unblacklist_key,
    unenumifier,
    update_qs_callback,
)

from .. import extra

selectbox_qs = extra(selectbox_qs)
multiselect_qs = extra(multiselect_qs)
radio_qs = extra(radio_qs)
text_area_qs = extra(text_area_qs)
text_input_qs = extra(text_input_qs)
number_input_qs = extra(number_input_qs)
checkbox_qs = extra(checkbox_qs)
make_query_string = extra(make_query_string)
update_qs_callback = extra(update_qs_callback)
add_qs_callback = extra(add_qs_callback)
clear_qs_callback = extra(clear_qs_callback)
unenumifier = extra(unenumifier)
from_query_args = extra(from_query_args)
from_query_args_index = extra(from_query_args_index)
blacklist_key = extra(blacklist_key)
unblacklist_key = extra(unblacklist_key)

# EXAMPLES -------------------------------------------------------------------
def example_text_input():
    import streamlit as st
    from streamlit_qs import text_input_qs

    st.markdown(
        "Click this URL: "
        "[?input_some_text=Hello+World](?input_some_text=Hello+World)"
    )
    text = text_input_qs("Enter Some Text", key="input_some_text")

    if text == "Hello World":
        st.success("Nice Job! Notice what happened in your browser's URL bar ☝️☝️☝️")


def example_multiselect():
    import streamlit as st

    st.markdown("[Click this URL](?multi=Streamlit&multi=QS&multi=Rocks#multi-select)")
    values = multiselect_qs(
        "Your opinion about this library:",
        options=["Streamlit", "QS", "Rocks", "I", "Don't", "Know"],
        default=["I", "Don't", "Know"],
        key="multi",
    )

    if values == ["Streamlit", "QS", "Rocks"]:
        st.success("That's Right!")


def example_options():
    selectbox_qs(
        "Select an option:",
        options=["A", "B", "C"],
        key="auto_select1",
        autoupdate=True,
    )
    radio_qs(
        "Select another option:",
        options=["A", "B", "C"],
        key="auto_select2",
        autoupdate=True,
    )


def example_permalink():
    import streamlit as st

    number_input_qs("Enter a number", key="number1", autoupdate=True)
    checkbox_qs("Click the checkbox", key="checkbox", autoupdate=True)
    st.markdown(
        f"You can make a permalink like this: [permalink](/{make_query_string()})"
    )


__title__ = "Query String"
__desc__ = "Utilities and Elements for interacting with the URL query string. Full example at  \n❓[query-string.streamlit.app](https://query-string.streamlit.app/)"
__icon__ = "❓"
__examples__ = {
    example_text_input: [text_input_qs],
    example_multiselect: [multiselect_qs],
    example_options: [selectbox_qs, radio_qs],
    example_permalink: [make_query_string, number_input_qs, checkbox_qs],
}
__author__ = "Alexander martin"
__github_repo__ = "Asaurus1/streamlit-qs"
__pypi_name__ = "streamlit-qs"
__package_name__ = "streamlit_qs"
