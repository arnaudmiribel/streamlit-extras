import ast
import html
import importlib
import inspect
import json
import pkgutil
from importlib import import_module, metadata
from pathlib import Path
from types import ModuleType
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

import mkdocs_gen_files

import streamlit_extras

extra_modules_names = [extra.name for extra in pkgutil.iter_modules(streamlit_extras.__path__) if extra.ispkg]


def get_stlite_wheel_url() -> str:
    version = metadata.version("streamlit-extras")
    release_url = f"https://pypi.org/pypi/streamlit-extras/{quote(version, safe='')}/json"
    with urlopen(release_url, timeout=10) as response:
        release = json.load(response)
    for distribution in release["urls"]:
        if distribution["packagetype"] != "bdist_wheel":
            continue
        url = distribution["url"]
        parsed = urlsplit(url)
        if (
            parsed.scheme == "https"
            and parsed.hostname == "files.pythonhosted.org"
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
            and parsed.path.endswith(f"/streamlit_extras-{version}-py3-none-any.whl")
        ):
            return url
    raise ValueError(f"No compatible PyPI wheel found for streamlit-extras {version}")


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
      href="https://cdn.jsdelivr.net/npm/@stlite/browser@1.8.1/build/stlite.css"
    >
  </head>
  <body>
    <div id="root"></div>
    <script type="module">
      import * as stlite from "https://cdn.jsdelivr.net/npm/@stlite/browser@1.8.1/build/stlite.js";
      if (window.location.search !== "?embed=true") {{
        window.location.search = "?embed=true";
      }}
      stlite.mount(
  {{
    requirements: [{wheel_url}],
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
<script src="https://cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.3.7/iframeResizer.min.js" integrity="sha512-JurjZFufyOjexPw9s5Eb1VRDauHh9/ZophxPxSHcdwc94xHIlzZEhS7O2HR7po0+VW5aQEiLwUsdxLfi9zcCgg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

<details class="extras-example">
    <summary>Output (beta)</summary>
    <div class="extras-example-frame">
        <iframe srcdoc="{}" id="iframe-{}" title="Interactive example: {}" height="400" loading="lazy"></iframe>
        <div class="extras-example-footer">
            <span>Powered by <a href="https://github.com/whitphx/stlite">stlite</a></span>
            <a href="https://streamlit.io/playground?template=blank&amp;code={}">Edit in playground</a>
        </div>
    </div>
</details>
"""

STLITE_CODE = """
from streamlit_extras.{extra_module_name} import *

with st.echo():
    {example_function}()
"""

STLITE_CODE_FOR_PLAYGROUND = """
from streamlit_extras.{extra_module_name} import *

{example_function_source}

{example_function_name}()
"""

EXTRA_EXAMPLE_MD_TEMPLATE = """
### `{func_name}`

```python
{func_source}
```
"""
EXTRA_FUNCTIONS_MD_TEMPLATE = """::: src.streamlit_extras.{module_name}.{func_name}

**Import:**

```python
from streamlit_extras.{module_name} import {func_name}
```
"""

EXTRA_MD_TEMPLATE = """*Submitted by {author}*

{description}

## Functions

{functions_docstrings}
"""

EXTRA_MD_TEMPLATE_IF_PYPI = """*Submitted by {author}*

{description}

Visit the [PyPI page](https://pypi.org/project/{pypi_name}/) for more information.
"""


def find_decorated_functions(module_name: str, decorator_name: str = "extra") -> list[str]:
    """
    Finds functions that are either decorated with @extra or in __funcs__
    We use this to identify the functions we want to show in the docs.

    Args:
        module_name (str): Name of the module
        decorator_name (str, optional): Name of the decorator. Defaults to "extra".

    Returns:
        List[str]: List of function names that use the extra decorator/wrapper
    """
    module = importlib.import_module(module_name)

    if hasattr(module, "__funcs__"):
        return [func.__name__ for func in module.__funcs__]

    decorated_functions = []

    assert module.__file__, f"Module {module_name} has no __file__ attribute"
    module_source = Path(module.__file__).read_text(encoding="utf-8")

    parsed_module = ast.parse(module_source)

    for node in ast.walk(parsed_module):
        if isinstance(node, ast.FunctionDef):
            decorated_functions.extend(
                node.name
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Name) and decorator.id == decorator_name
            )

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
        "inputs": getattr(module, "__inputs__", {}),
        "description": module.__desc__,
        "author": module.__author__,
        "github_repo": getattr(module, "__github_repo__", None),
        "streamlit_cloud_url": getattr(module, "__streamlit_cloud_url__", None),
        "pypi_name": getattr(module, "__pypi_name__", None),
        "package_name": getattr(module, "__package_name__", None),
        "twitter_username": getattr(module, "__twitter_username__", None),
        "buymeacoffee_username": getattr(module, "__buymeacoffee_username__", None),
        "forum_url": getattr(module, "__forum_url__", None),
        "pretty_title": module.__icon__ + "\u00a0" * 3 + module.__title__,
        "module_name": module_name,
        "decorated_functions": find_decorated_functions(f"streamlit_extras.{module_name}"),
        "playground": getattr(module, "__playground__", False),
        "deprecated": getattr(module, "__deprecated__", False),
    }


def generate_hash_for_playground_url(source_code: str) -> str:
    import base64
    import gzip
    import re

    # Pre-fix source code with 'import streamlit_extras'
    # To trigger the download of the package in the playground
    source_code = "import streamlit_extras\n" + source_code

    # Compress the content using gzip
    compressed = gzip.compress(source_code.encode("utf-8"))

    # Convert compressed data to base64
    base64_encoded = base64.b64encode(compressed).decode("utf-8")

    # Make URL-safe by replacing + with -, / with _, and removing padding '='
    return re.sub(
        r"[\+\/=]",
        lambda x: "-" if x.group(0) == "+" else "_" if x.group(0) == "/" else "",
        base64_encoded,
    )


wheel_url = None
for extra_module_name in extra_modules_names:
    mod = import_module(f"streamlit_extras.{extra_module_name}")
    extra_metadata = get_extra_metadata(mod, extra_module_name)
    if extra_metadata.get("deprecated"):
        full_doc_path = Path(f"extras_deprecated/{extra_module_name}.md")
    else:
        full_doc_path = Path(f"extras/{extra_module_name}.md")

    decorated_functions = extra_metadata.get("decorated_functions", [])
    extra_metadata["functions_docstrings"] = "\n\n".join(
        EXTRA_FUNCTIONS_MD_TEMPLATE.format(module_name=extra_module_name, func_name=decorated_function)
        for decorated_function in decorated_functions
    )

    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        template = EXTRA_MD_TEMPLATE_IF_PYPI if extra_metadata.get("pypi_name") else EXTRA_MD_TEMPLATE

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

                if extra_metadata["playground"]:
                    if wheel_url is None:
                        wheel_url = json.dumps(get_stlite_wheel_url())
                    stlite_html = STLITE_HTML_TO_IFRAME.format(
                        wheel_url=wheel_url,
                        code=STLITE_CODE.format(
                            extra_module_name=extra_module_name,
                            example_function=example_function.__name__,
                        ),
                    ).strip()

                    iframe_html = STLITE_IFRAME_HTML.format(
                        html.escape(stlite_html),
                        example_function.__name__,
                        html.escape(example_function.__name__, quote=True),
                        generate_hash_for_playground_url(
                            STLITE_CODE_FOR_PLAYGROUND.format(
                                extra_module_name=extra_module_name,
                                example_function_source=func_source,
                                example_function_name=example_function.__name__,
                            )
                        ),
                    )

                    example_function_names.append(example_function.__name__)

                    print(iframe_html, file=f)

            if extra_metadata["playground"]:
                # This is needed to have all iframes auto-resize
                auto_size_iframe_html = "<script>\n"
                for example_function_name in example_function_names:
                    auto_size_iframe_html += (
                        f'iFrameResize({{ log: true, checkOrigin: false }}, "#iframe-{example_function_name}")\n'
                    )
                auto_size_iframe_html += "</script>"

            print(auto_size_iframe_html, file=f)

    mkdocs_gen_files.set_edit_path(full_doc_path, "generate.py")
