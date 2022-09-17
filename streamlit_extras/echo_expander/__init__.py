import contextlib
import textwrap
import traceback
from typing import List

import streamlit as st

###
# Extension from echo() in streamlit/echo.py
###


@contextlib.contextmanager
def echo_expander(code_location="above", expander=True, label="Show code"):
    """Use in a `with` block to draw some code on the app, then execute it.

    Parameters
    ----------
    code_location : "above" or "below"
        Whether to show the echoed code before or after the results of the
        executed code block.
        Default is "above"
    expander : Boolean
        Whether the code block should occur in an expander.
        If False, then same as `st.echo`
        Default is True
    label : Text
        If expander is True, then the label for the expander.
        Default is "Show code"

    Example
    -------

    >>> with st.echo():
    >>>     st.write('This code will be printed')

    >>> with st.echo_expander(code_location="below", expander=True, label="Expand to see the code"):
    >>>     st.write('This code will be printed in an expander')

    """

    from streamlit import empty, source_util
    from streamlit.echo import _get_indent, _get_initial_indent

    if code_location == "above":
        placeholder = empty()
    else:
        placeholder = st

    try:
        # Get stack frame *before* running the echoed code. The frame's
        # line number will point to the `st.echo` statement we're running.
        frame = traceback.extract_stack()[-3]
        filename, start_line = frame.filename, frame.lineno

        # Read the file containing the source code of the echoed statement.
        with source_util.open_python_file(filename) as source_file:
            source_lines = source_file.readlines()

        # Get the indent of the first line in the echo block, skipping over any
        # empty lines.
        initial_indent = _get_initial_indent(source_lines[start_line:])

        # Iterate over the remaining lines in the source file
        # until we find one that's indented less than the rest of the
        # block. That's our end line.
        #
        # Note that this is *not* a perfect strategy, because
        # de-denting is not guaranteed to signal "end of block". (A
        # triple-quoted string might be dedented but still in the
        # echo block, for example.)
        # TODO: rewrite this to parse the AST to get the *actual* end of the block.
        lines_to_display: List[str] = []
        for line in source_lines[start_line:]:
            indent = _get_indent(line)
            if indent is not None and indent < initial_indent:
                break
            lines_to_display.append(line)

        code_string = textwrap.dedent("".join(lines_to_display))

        # Run the echoed code...
        yield

        # And draw the code string to the app!
        if expander:
            placeholder.expander(label).code(code_string, "python")
        else:
            placeholder.code(code_string, "python")

    except FileNotFoundError as err:
        placeholder.warning("Unable to display code. %s" % err)


def example1():
    with echo_expander():
        import streamlit as st

        st.markdown(
            """
            This component is a combination of `st.echo` and `st.expander`.
            The code inside the `with echo_expander()` block will be executed,
            and the code can be shown/hidden behind an expander
            """
        )


def example2():
    with echo_expander(
        code_location="below", label="Simple Dataframe example"
    ):
        import pandas as pd
        import streamlit as st

        df = pd.DataFrame(
            [[1, 2, 3, 4, 5], [11, 12, 13, 14, 15]],
            columns=("A", "B", "C", "D", "E"),
        )
        st.dataframe(df)


__func__ = echo_expander
__title__ = "Echo Expander"
__desc__ = (
    "Execute code, and show the code that was executed, but in an expander."
)
__icon__ = "🆒"
__examples__ = [example1, example2]
__experimental_playground__ = False
