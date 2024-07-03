import datetime
import enum
import time
from functools import wraps
from sys import exc_info
from threading import Thread
from types import TracebackType

import streamlit as st
from streamlit.errors import StreamlitAPIException
from streamlit.runtime.caching.cache_utils import _make_value_key
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

from .. import extra


class _Status(enum.Enum):
    """The function cache types we implement."""

    RUNNING = "RUNNING"
    JUST_FINISHED = "JUST_FINISHED"
    COMPLETE = "COMPLETE"


class _ThreadState:
    def __init__(self):
        self.status: _Status = None
        self.thread: Thread = None
        self.init_time: datetime.datetime = None
        self.error: Exception = None
        self.error_traceback: TracebackType = None
        self.current_return = None
        self.latest_return = None


# Set to None to skip initial cache check, or a higher value for longer delay
CACHE_DELAY_MS = 10


@extra
def async_load(
    *,
    poll_interval=0.5,
    refresh_every=None,
    key=None,
):
    """Decorator to run a function in the background, and update the app on completion.

    When you call a function decorated with `@async_load()`, it will initially
    return `None` while the function executes asynchronously. A fragment will
    periodically execute to check when the function completes.

    Once the function completes, the app will do a full rerun, and this time the
    function will return whatever return value or raise an error. The return value
    is stored in session state and re-used on any subsequent reruns.

    Similar to st.cache_data, calling the function repeatedly with different
    arguments or key will result in separate background threads and return values.
    The same arguments + key will always be treated as the same run / thread.

    If you set `refresh_every=`, the function is automatically rerun async on the
    specified interval, and the return value is updated on complete.

    Args:
        func (Callable): The function to load in the background.
        poll_interval (float, optional): How often to check if the function completed once it starts running.
        key (str, optional): A key to store the return value in session_state.
        refresh_every(int, optional): If set, the function will be re-executed and return value refreshed
            at the specified interval. This is based on the _start time_, not the
            end time (so it should refresh every interval, not every exec_time + interval)
    """
    if not hasattr(st, "fragment"):
        raise ImportError("async_load requires Streamlit >=1.37 for st.fragment")

    def outer_decorator(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            # Use Streamlit caching hash to generate a unique key
            KEY_INTERMEDIATE = _make_value_key(
                cache_type="ASYNC_LOAD",
                func=func,
                func_args=args,
                func_kwargs=kwargs,
                hash_funcs=None,
            )
            KEY_INTERMEDIATE = f"ASYNC_LOAD_STATE_{KEY_INTERMEDIATE}"
            if key:
                KEY_INTERMEDIATE = f"{KEY_INTERMEDIATE}_{key}"

            # Track the state of a given thread in session_state
            if KEY_INTERMEDIATE not in st.session_state:
                st.session_state[KEY_INTERMEDIATE] = _ThreadState()
            state: _ThreadState = st.session_state[KEY_INTERMEDIATE]
            placeholder = st.container()

            # If no status, we need to start a new run (first time or refresh)
            if state.status is None:
                # wrapper to call the function and store return value or error in state
                def wrapper():
                    state: _ThreadState = st.session_state[KEY_INTERMEDIATE]
                    try:
                        state.current_return = func(*args, **kwargs)
                    except Exception as e:
                        _, _, traceback = exc_info()
                        state.error = e
                        state.error_traceback = traceback

                # Start the thread and update the state
                t = Thread(target=wrapper)
                add_script_run_ctx(t, get_script_run_ctx())
                state.thread = t
                t.start()
                state.status = _Status.RUNNING
                state.init_time = datetime.datetime.now()

                # Do a quick check to see if the function returns immediately
                # (Such as due to caching)
                if CACHE_DELAY_MS:
                    time.sleep(CACHE_DELAY_MS / 1000)
                    if not state.thread.is_alive():
                        state.status = _Status.JUST_FINISHED

            # If the thread is currently running, check the status
            if state.status == _Status.RUNNING:

                @st.fragment(run_every=poll_interval)
                def check_status(state_key):
                    # If the thread finished, update status for next run
                    state: _ThreadState = st.session_state[state_key]
                    if not state.thread.is_alive():
                        state.status = _Status.JUST_FINISHED
                        st.rerun()

                with placeholder:
                    check_status(KEY_INTERMEDIATE)

            # If the thread just finished, record the result
            if state.status == _Status.JUST_FINISHED:
                if state.error is not None:
                    # TODO: Probably some way to clean up the trace even better
                    raise state.error.with_traceback(state.error_traceback)
                if state.current_return is not None:
                    # Make the latest value available during reruns
                    state.latest_return = state.current_return
                    if key:
                        st.session_state[key] = state.current_return
                    state.current_return = None
                    state.status = _Status.COMPLETE
                else:
                    raise StreamlitAPIException(
                        "Async function exited unexpectedly without return value"
                    )

            # Set a refresh timer if status is complete and this is configured
            # (otherwise, COMPLETE is the end state, do nothing except return)
            if state.status == _Status.COMPLETE and refresh_every:
                # TODO: try calculating this run_every time more precisely
                @st.fragment(run_every=refresh_every / 3)
                def refresh_timer(state_key):
                    # Subtract a small amount to reduce risk of an extra call
                    state: _ThreadState = st.session_state[state_key]
                    diff = datetime.timedelta(seconds=refresh_every, milliseconds=-200)
                    if datetime.datetime.now() >= state.init_time + diff:
                        state.status = None
                        state.error = None
                        st.rerun()

                with placeholder:
                    refresh_timer(KEY_INTERMEDIATE)

            # Will be `None` on initial run, or latest completed value
            # This always runs unless there's an exception or JUST_FINISHED rerun()
            return state.latest_return

        return decorator

    return outer_decorator


def hide_running_man():
    st.html(
        """
        <style>
        [data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
            }
        </style>
        """,
    )


def example():
    import time

    import numpy as np
    import pandas as pd

    hide_running_man()

    "`refresh_data()` runs in the background, so these widgets remain fully interactive"
    st.button("Button 1")

    st.slider("Random slider", 0, 100)

    @async_load(refresh_every=4)
    def refresh_data(x=1, sleep=2):
        time.sleep(sleep)
        return pd.DataFrame(
            np.random.randn(5, 5) * x, columns=["a", "b", "c", "d", "e"]
        )

    df = refresh_data()
    if df is not None:
        "The dataframe updates every few seconds"
        st.dataframe(df)
    else:
        "Show a skeleton while initial load runs async"
        st._main._skeleton()


__title__ = "Async Load"
__desc__ = (
    "Decorator to run a function in the background, and update the app on completion."
)
__icon__ = "♻️"
__examples__ = [example]
__author__ = "Joshua Carroll"
__experimental_playground__ = False
