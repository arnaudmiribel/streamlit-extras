import ast
import html
import importlib
import inspect
import pkgutil
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

import mkdocs_gen_files
import streamlit_extras

extra_modules_names = [
    extra.name for extra in pkgutil.iter_modules(streamlit_extras.__path__)
]

STLITE_HTML_TO_IFRAME = """
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />
    <title>Embedded Streamlit App</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/@stlite/mountable/build/stlite.css"
    >
  </head>
  <body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable/build/stlite.js"></script>
    <script>
      if (window.location.search !== "?embed=true") {{
        window.location.search = "?embed=true";
      }}
      stlite.mount(
  {{
    requirements: ["streamlit", "streamlit-extras"], // Packages to install
    entrypoint: "streamlit_app.py",
    files: {{
      "streamlit_app.py": `
import streamlit as st

st.markdown('<style>[data-baseweb~="modal"]{{visibility: hidden;}}</style>', unsafe_allow_html=True,)

{code}
`,
    }},
  }},
        document.getElementById("root")
      );
    </script>
  </body>
</html>
"""

code = """
from streamlit_extras.stoggle import stoggle

stoggle("This is just a...", "secret!")
"""

STLITE_IFRAME_HTML = """
<style>
    .container {{
            width: 100%;
            background-color: #fff;/* #f2f2f2;  */
            border-radius: 2px;
            margin-top: 20px;
            border: 1px solid #f2f2f2; /* Thin border on left, top, and right */
    }}

    .content {{
        padding: 20px;
    }}

    .banner {{
        background-color: #f2f2f2;
        text-align: center;
        padding: 10px 0; /* Adjust padding to reduce height */
        border-radius: 2px;
    }}

    .banner p {{
        margin: 0;
    }}

    .banner a {{
        text-decoration: none;
        color: #007bff;
    }}

    iframe {{
        overflow: scroll;
    }}
</style>

<script src="https://cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.3.7/iframeResizer.min.js" integrity="sha512-JurjZFufyOjexPw9s5Eb1VRDauHh9/ZophxPxSHcdwc94xHIlzZEhS7O2HR7po0+VW5aQEiLwUsdxLfi9zcCgg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

<details class="example">
    <summary> Output (beta)</summary>
    <div class="container">
        <div class="content">
            <iframe srcdoc="{}" width="100%" id="iframe-{}" height="400" frameBorder="0" overflow="scroll"> <p> Just trying stuff </p> </iframe>
        </div>
        <div class="banner">
                <p style="text-align: right; margin-right: 20px;">🎈 Powered by <a href="https://github.com/whitphx/stlite">stlite</a></p>
        </div>
    </div>
</details>
"""

STLITE_CODE = """
from streamlit_extras.{extra_module_name} import *

with st.echo():
    {example_function}()
"""

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


def find_decorated_functions(
    module_name: str, decorator_name: str = "extra"
) -> List[str]:
    """
    Parses a module to find out which functions are decorated with a given decorator
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

    assert module.__file__, f"Module {module_name} has no __file__ attribute"

    with open(module.__file__, "r") as module_file:
        module_source = module_file.read()

    parsed_module = ast.parse(module_source)

    for node in ast.walk(parsed_module):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
                    decorated_functions.append(node.name)

    return decorated_functions


def get_extra_metadata(module: ModuleType, module_name: str) -> dict:
    """
    Collect extra metadata from the module

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
        "experimental_playground": getattr(
            module, "__experimental_playground__", False
        ),
        "experimental_playground_funcs": getattr(
            module, "__experimental_playground_funcs__", None
        ),
        "pretty_title": module.__icon__ + "  " + module.__title__,
        "module_name": module_name,
        "decorated_functions": find_decorated_functions(
            f"streamlit_extras.{module_name}"
        ),
        "stlite": getattr(module, "__stlite__", True),
    }


for extra_module_name in extra_modules_names:
    mod = import_module(f"streamlit_extras.{extra_module_name}")
    extra_metadata = get_extra_metadata(mod, extra_module_name)

    full_doc_path = Path(f"extras/{extra_module_name}.md")

    decorated_functions = extra_metadata.get("decorated_functions", [])
    extra_metadata["functions_docstrings"] = "--- \n".join(
        EXTRA_FUNCTIONS_MD_TEMPLATE.format(
            module_name=extra_module_name, func_name=decorated_function
        )
        for decorated_function in decorated_functions
    )

    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        template = (
            EXTRA_MD_TEMPLATE_IF_PYPI
            if extra_metadata.get("pypi_name")
            else EXTRA_MD_TEMPLATE
        )

        print(template.format(**extra_metadata), file=f)

        example_function_names = []
        if extra_metadata["examples"]:
            print("## Examples", file=f)
            for example_function in extra_metadata["examples"]:
                func_source = inspect.getsource(example_function)
                print(
                    EXTRA_EXAMPLE_MD_TEMPLATE.format(
                        func_name=example_function.__name__,
                        func_source=func_source,
                    ),
                    file=f,
                )

                if extra_metadata["stlite"]:

                    stlite_html = STLITE_HTML_TO_IFRAME.format(
                        code=STLITE_CODE.format(
                            extra_module_name=extra_module_name,
                            example_function=example_function.__name__,
                        )
                    ).strip()

                    iframe_html = STLITE_IFRAME_HTML.format(
                        html.escape(stlite_html),
                        example_function.__name__,
                    )

                    example_function_names.append(example_function.__name__)

                    print(iframe_html, file=f)

            if extra_metadata["stlite"]:
                # This is needed to have all iframes auto-resize
                auto_size_iframe_html = "<script>\n"
                for example_function_name in example_function_names:
                    auto_size_iframe_html += f'iFrameResize({{ log: true, checkOrigin: false }}, "#iframe-{example_function_name}")\n'
                auto_size_iframe_html += "</script>"

            print(auto_size_iframe_html, file=f)

    mkdocs_gen_files.set_edit_path(full_doc_path, "generate.py")
