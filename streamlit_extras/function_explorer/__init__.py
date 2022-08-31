import inspect
import random
from typing import Callable

import pandas as pd
import streamlit as st
from st_keyup import st_keyup


def get_args(func):
    signature = inspect.signature(func)
    return [
        dict(argument=k, type_hint=v.annotation, default=v.default)
        for k, v in signature.parameters.items()
    ]


def is_empty(argument_attribute):
    return argument_attribute is inspect.Parameter.empty


def get_arg_from_session_state(func_name: str, argument: str):
    if func_name in st.session_state:
        if "inputs" in st.session_state[func_name]:
            return st.session_state[func_name]["inputs"][argument]


def function_explorer(func: Callable):
    """Gives a Streamlit UI to any function.

    Args:
        func (callable): Python function
    """

    args = get_args(func)
    inputs = dict()

    st.write("#### Inputs")
    st.write(
        f"Go ahead and play with `{func.__name__}` parameters, see how"
        " they change the output!"
    )

    for argument_info in args:
        argument, type_hint, default = argument_info.values()
        label = argument if not is_empty(default) else f"{argument}*"

        if is_empty(type_hint):
            default = (
                get_arg_from_session_state(func.__name__, argument) or default
                if not is_empty(default)
                else "Sample string"
            )
            inputs[argument] = st.text_input(label, value=default)
        else:
            label += f" ({type_hint.__name__})"
            if type_hint == int:
                default = get_arg_from_session_state(
                    func.__name__, argument
                ) or (default if not is_empty(default) else 12)
                inputs[argument] = st.number_input(
                    label, step=1, value=default
                )
            elif type_hint == float:
                default = (
                    get_arg_from_session_state(func.__name__, argument)
                    or default
                    if not is_empty(default)
                    else 12.0
                )
                inputs[argument] = st.number_input(label, value=default)
            elif type_hint == str:
                default = (
                    get_arg_from_session_state(func.__name__, argument)
                    or default
                    if not is_empty(default)
                    else "Sample string"
                )
                inputs[argument] = st_keyup(label, value=default)
            elif type_hint == bool:
                default = (
                    get_arg_from_session_state(func.__name__, argument)
                    or default
                    if not is_empty(default)
                    else True
                )
                inputs[argument] = st.checkbox(label, value=default)
            elif type_hint == pd.DataFrame:
                inputs[argument] = get_arg_from_session_state(
                    func.__name__, argument
                ) or pd.DataFrame(["abcde"])
            else:
                st.warning(
                    f"`function_explorer` does not support type {type_hint}"
                )

    st.write("#### Output")
    func(**inputs)
    if func.__name__ not in st.session_state:
        st.session_state[func.__name__] = {}
    st.session_state[func.__name__]["inputs"] = inputs


def example():
    def foo(
        age: int, name: str, image_url: str = "http://placekitten.com/120/120"
    ):
        st.write(f"Hey! My name is {name} and I'm {age} years old")
        st.write("Here's a picture")
        st.image(image_url)

    function_explorer(foo)


__func__ = function_explorer
__title__ = "Function explorer"
__desc__ = "Give a UI to any Python function! Very alpha though"
__icon__ = "👩‍🚀"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__streamlit_cloud_url__ = None
__github_repo__ = None
