import inspect
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any, Optional, TypeVar, Union, overload

from streamlit.runtime.metrics_util import gather_metrics as _gather_metrics

from streamlit_extras.version import (
    STREAMLIT_EXTRAS_VERSION_STRING as _STREAMLIT_EXTRAS_VERSION_STRING,
)

__version__ = _STREAMLIT_EXTRAS_VERSION_STRING


F = TypeVar("F", bound=Callable[..., Any])

# Typing overloads here are actually required so that you can correctly (= with correct typing) use the decorator in different ways:
#   1) as a decorator without parameters @extra
#   2) as a decorator with parameters (@extra(foo="bar") but this also refers to empty parameters @extra()
#   3) as a function: extra(my_function)


@overload
def extra(
    func: F,
) -> F: ...


@overload
def extra(
    func: None = None,
) -> Callable[[F], F]: ...


def extra(
    func: F | None = None,
) -> Callable[[F], F] | F:
    if func:
        filename = inspect.stack()[1].filename
        submodule = Path(filename).parent.name
        extra_name = "streamlit_extras." + submodule
        module = import_module(extra_name)

        if hasattr(module, "__funcs__"):
            module.__funcs__ += [func]  # type: ignore[attr-defined]
        else:
            module.__funcs__ = [func]  # type: ignore[attr-defined]

        profiling_name = f"{submodule}.{func.__name__}"
        return _gather_metrics(name=profiling_name, func=func)

    def wrapper(f: F) -> F:
        return f

    return wrapper
