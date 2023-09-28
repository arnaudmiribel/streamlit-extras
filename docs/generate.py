import inspect
import pkgutil
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

import mkdocs_gen_files

import streamlit_extras

# TODO: Check why query_string fails
extra_modules_names = [
    extra.name
    for extra in pkgutil.iter_modules(streamlit_extras.__path__)
    if extra.name != "query_string"
]

EXTRA_EXAMPLE_MD_TEMPLATE = """
### `{func_name}`
``` py
{func_source}
```
"""
EXTRA_FUNCTIONS_MD_TEMPLATE = """
### `{func_name}`

#### ::: src.streamlit_extras.{module_name}.{func_name}

**Import:**

``` py
from streamlit_extras.{module_name} import {func_name} # (1)!
```

1. You should add this to the top of your .py file :hammer_and_wrench:

"""

EXTRA_MD_TEMPLATE = """

# {pretty_title}

Submitted by **{author}**

## Summary
{description}

## Functions
{functions_docstrings}


"""

EXTRA_MD_TEMPLATE_IF_PYPI = """

# {pretty_title}

Submitted by **{author}**

## Summary
{description}

## Docstring
Visit the [PyPI page](https://pypi.org/project/{pypi_name}/) for more information.
"""


import ast
import importlib


def find_decorated_functions(module_name: str, decorator_name: str = "extra") -> List[str]:
    """Parses a module to find out which functions are decorated with a given decorator
    We use this to identify the functions we want to show in the docs, which are
    decorated with `@extra`.

    Args:
        module_name (str): Name of the module
        decorator_name (str, optional): Name of the decorator. Defaults to "extra".

    Returns:
        List[str]: Decorated functions with @decorator_name
    """
    module = importlib.import_module(module_name)
    decorated_functions = []

    with open(module.__file__, "r") as module_file:
        module_source = module_file.read()

    parsed_module = ast.parse(module_source)

    for node in ast.walk(parsed_module):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
                    decorated_functions.append(node.name)

    return decorated_functions


def find_example_functions(module_name: str) -> List[str]:
    """Parses a module to find out which functions are examples.
    They should start with `example_`

    Args:
        module_name (str): Name of the module
        decorator_name (str, optional): Name of the decorator. Defaults to "extra".

    Returns:
        List[str]: Example function names
    """
    module = importlib.import_module(module_name)
    example_functions = []

    with open(module.__file__, "r") as module_file:
        module_source = module_file.read()

    parsed_module = ast.parse(module_source)

    for node in ast.walk(parsed_module):
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("example_"):
                example_functions.append(node.name)

    return example_functions


def get_extra_metadata(module: ModuleType, module_name: str) -> dict:
    """Collect extra metadata from the module

    Args:
        module (ModuleType): Module of the extra
        module_name (str): Name of the extra

    Returns:
        dict: Dictionary with all the metadata of the extra
    """
    return {
        "title": module.__title__,
        "icon": module.__icon__,
        "funcs": module.__funcs__,
        "examples": module.__examples__,
        "inputs": getattr(module, "__inputs__", dict()),
        "description": module.__desc__,
        "author": module.__author__,
        "github_repo": getattr(module, "__github_repo__", None),
        "streamlit_cloud_url": getattr(module, "__streamlit_cloud_url__", None),
        "pypi_name": getattr(module, "__pypi_name__", None),
        "package_name": getattr(module, "__package_name__", None),
        "twitter_username": getattr(module, "__twitter_username__", None),
        "buymeacoffee_username": getattr(module, "__buymeacoffee_username__", None),
        "forum_url": getattr(module, "__forum_url__", None),
        "experimental_playground": getattr(module, "__experimental_playground__", False),
        "experimental_playground_funcs": getattr(module, "__experimental_playground_funcs__", None),
        "pretty_title": module.__icon__ + "  " + module.__title__,
        "module_name": module_name,
        "decorated_functions": find_decorated_functions(f"streamlit_extras.{module_name}"),
        "example_functions": find_example_functions(f"streamlit_extras.{module_name}"),
    }


for extra_module_name in extra_modules_names:
    mod = import_module(f"streamlit_extras.{extra_module_name}")
    extra_metadata = get_extra_metadata(mod, extra_module_name)

    full_doc_path = Path(f"extras/{extra_module_name}.md")

    extra_metadata["functions_docstrings"] = "--- \n".join(
        EXTRA_FUNCTIONS_MD_TEMPLATE.format(
            module_name=extra_module_name, func_name=decorated_function
        )
        for decorated_function in extra_metadata.get("decorated_functions")
    )

    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        template = (
            EXTRA_MD_TEMPLATE_IF_PYPI if extra_metadata.get("pypi_name") else EXTRA_MD_TEMPLATE
        )

        print(template.format(**extra_metadata), file=f)

        if extra_metadata["example_functions"]:
            print("## Examples", file=f)
            for example_function in extra_metadata["example_functions"]:
                print(
                    EXTRA_EXAMPLE_MD_TEMPLATE.format(
                        func_name=example_function,
                        func_source=inspect.getsource(getattr(mod, example_function)),
                    ),
                    file=f,
                )

    mkdocs_gen_files.set_edit_path(full_doc_path, "generate.py")
