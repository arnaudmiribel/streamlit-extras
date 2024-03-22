"""DOCSTRING HERE"""
from __future__ import annotations

import time

import streamlit as st

from .. import extra

from collections import Counter
from functools import wraps, partial
from dataclasses import dataclass

from types import FunctionType
from typing import Any
import sys
import hashlib
import inspect
from threading import Semaphore, Lock, Condition


@dataclass
class FuncConcurrencyInfo:
    semaphore: Semaphore
    condition: Condition


SEMAPHORES_LOCK = Lock()
CONCURRENCY_MAP: dict[str, FuncConcurrencyInfo] = {}

COUNTERS = Counter()


def _make_function_key(func: FunctionType, max_concurrency: int) -> str:
    """Create the unique key for a function's cache.
    A function's key is stable across reruns of the app, and changes when
    the function's source code changes.
    """

    hashlib_kwargs: dict[str, Any] = (
        {"usedforsecurity": False} if sys.version_info >= (3, 9) else {}
    )
    func_hasher = hashlib.new("md5", **hashlib_kwargs)

    func_hasher.update(func.__module__.encode("utf-8"))
    func_hasher.update(func.__qualname__.encode("utf-8"))

    try:
        source_code = inspect.getsource(func).encode("utf-8")
    except OSError:
        source_code = func.__code__.co_code

    func_hasher.update(source_code)
    func_hasher.update(max_concurrency.to_bytes(4, byteorder="big"))

    return func_hasher.hexdigest()


@extra
def concurrency_limiter(func=None, max_concurrency: int = 1, show_spinner: bool = True):
    """Decorator that limits function concurrent execution in Stremalit app."""

    if func is None:
        return partial(
            concurrency_limiter,
            max_concurrency=max_concurrency,
            show_spinner=show_spinner,
        )

    function_key = _make_function_key(func, max_concurrency)

    with SEMAPHORES_LOCK:
        if function_key not in CONCURRENCY_MAP:
            CONCURRENCY_MAP[function_key] = FuncConcurrencyInfo(
                semaphore=Semaphore(max_concurrency),
                condition=Condition(),
            )

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_info = CONCURRENCY_MAP[function_key]
        acquired = False

        COUNTERS.update({function_key: 1})

        try:
            with func_info.condition:
                while not (acquired := func_info.semaphore.acquire(blocking=False)):
                    if show_spinner:
                        with st.spinner(
                                f"""Function {func.__name__} has approximately
                            {COUNTERS[function_key] - max_concurrency} instances
                            waiting...""",
                                _cache=True,
                        ):

                            func_info.condition.wait()
                    else:
                        func_info.condition.wait()

            return func(*args, **kwargs)
        finally:
            COUNTERS.update({function_key: -1})
            with func_info.condition:
                if acquired:
                    func_info.semaphore.release()
                func_info.condition.notify_all()

    return wrapper


def example():
    @concurrency_limiter(max_concurrency=1)
    def heavy_computation():
        st.write("Heavy computation")
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.15)
            my_bar.progress(percent_complete + 1, text=progress_text)
        st.write("END OF Heavy computation")
        return 42

    my_button = st.button("Run heavy computation")

    if my_button:
        heavy_computation()


__title__ = "Concurrency limiter for your Streamlit app"
__desc__ = """This decorator limit function execution concurrency with max_concurrency param."""
__icon__ = "🚦"
__examples__ = [example]
__author__ = "Karen Javadyan"
__experimental_playground__ = False
