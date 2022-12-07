import pandas as pd


def test_args():
    from streamlit_extras.no_default_selectbox import _transform_arguments

    no_selection_label, args, kwargs = _transform_arguments(
        "Select a value", ["a", "b", "c"], no_selection_label="None"
    )

    assert no_selection_label == "None"
    assert args == ["Select a value"]
    assert kwargs == {"options": ["None", "a", "b", "c"]}


def test_kwargs():
    from streamlit_extras.no_default_selectbox import _transform_arguments

    no_selection_label, args, kwargs = _transform_arguments(
        label="Select a value", options=["a", "b", "c"]
    )

    assert no_selection_label == "---"
    assert args == []
    assert kwargs == {"label": "Select a value", "options": ["---", "a", "b", "c"]}


def test_args_with_kwargs():
    from streamlit_extras.no_default_selectbox import _transform_arguments

    no_selection_label, args, kwargs = _transform_arguments(
        "Select a value", ["a", "b", "c"], default="b", no_selection_label="None"
    )

    assert no_selection_label == "None"
    assert args == ["Select a value"]
    assert kwargs == {"options": ["None", "a", "b", "c"], "default": "b"}


def test_args_with_tuple():
    from streamlit_extras.no_default_selectbox import _transform_arguments

    no_selection_label, args, kwargs = _transform_arguments(
        "Select a value", ("a", "b", "c")
    )

    assert no_selection_label == "---"
    assert args == ["Select a value"]
    assert kwargs == {"options": ["---", "a", "b", "c"]}


def test_args_with_series():
    from streamlit_extras.no_default_selectbox import _transform_arguments

    no_selection_label, args, kwargs = _transform_arguments(
        "Select a value", pd.Series(["a", "b", "c"])
    )

    assert no_selection_label == "---"
    assert args == ["Select a value"]
    assert kwargs == {"options": ["---", "a", "b", "c"]}


def test_args_with_dataframe():
    from streamlit_extras.no_default_selectbox import _transform_arguments

    no_selection_label, args, kwargs = _transform_arguments(
        "Select a value", pd.DataFrame(["a", "b", "c"])
    )

    assert no_selection_label == "---"
    assert args == ["Select a value"]
    assert kwargs == {"options": ["---", "a", "b", "c"]}
