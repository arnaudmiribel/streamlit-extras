import streamlit as st

from streamlit_extras import extra


@extra
def selectbox(*args, **kwargs):
    """A selectbox that returns None unless the user has explicitly selected one of the
    options.

    All arguments are passed to st.selectbox except for `no_selection_label`, which is
    used to specify the label of the option that represents no selection.

    Parameters
    ----------
    no_selection_label : str
        The label to use for the no-selection option. Defaults to "---".
    """
    no_selection_label = kwargs.pop("no_selection_label", "---")

    args = list(args)

    # Get the options from either the args or kwargs
    try:
        options = args.pop(1)
    except IndexError:
        options = kwargs["options"]

    # Prepend the no-selection option to the list of options
    if no_selection_label not in options:
        options = [no_selection_label] + options
        kwargs["options"] = options

    result = st.selectbox(*args, **kwargs)
    if result == no_selection_label:
        return None
    return result


def example():
    st.write(
        """
        This is an example of a selectbox that returns None unless the user has
        explicitly selected one of the options.
        """
    )
    st.write(
        """
        The selectbox below has no default value, so it will return None until the
        user selects an option.
        """
    )
    result = selectbox("Select an option", ["A", "B", "C"])
    st.write("Result:", result)


__title__ = "No-Default Selectbox"
__desc__ = """
Just like st.selectbox, but with no default value -- returns None if nothing is selected.

Meant to be a solution to https://github.com/streamlit/streamlit/issues/949
"""
__icon__ = "🗳️"
__examples__ = [example]
__author__ = "Zachary Blackwood"
__experimental_playground__ = False
