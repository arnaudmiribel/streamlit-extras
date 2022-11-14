import inspect
from importlib import import_module
from typing import Any, Callable, Optional, TypeVar, Union, overload

from streamlit import _gather_metrics

F = TypeVar("F", bound=Callable[..., Any])


@overload
def extra(
    func: F,
) -> F:
    ...


@overload
def extra(
    func: None = None,
) -> Callable[[F], F]:
    ...


def extra(
    func: Optional[F] = None,
) -> Union[Callable[[F], F], F]:

    if func:

        filename = inspect.stack()[1].filename
        extra_name = "streamlit_extras." + filename.split("/")[-2]
        module = import_module(extra_name)

        if hasattr(module, "__funcs__"):
            module.__funcs__ += [func]  # type: ignore
        else:
            module.__funcs__ = [func]  # type: ignore

        name = f"{module}.{func.__name__}"
        return _gather_metrics(name=name, func=func)

    def wrapper(f: F) -> F:
        return f

    return wrapper
