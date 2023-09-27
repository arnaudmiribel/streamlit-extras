import pkgutil
from importlib import import_module
from pathlib import Path

import mkdocs_gen_files

import streamlit_extras

extra_names = [
    extra.name
    for extra in pkgutil.iter_modules(streamlit_extras.__path__)
    if extra.name != "query_string"
]

EXTRA_MD_TEMPLATE = """

# {extra_title}

Submitted by **{extra_author}**

## Summary
{description}

## Docstring

::: src.streamlit_extras.{extra_name}
    show_docstring_parameters: true
    show_types_in_signature: true

"""

# nav = mkdocs_gen_files.Nav()

for extra_name in extra_names:
    mod = import_module(f"streamlit_extras.{extra_name}")
    title = mod.__title__
    icon = mod.__icon__
    funcs = mod.__funcs__
    examples = mod.__examples__
    inputs = getattr(mod, "__inputs__", dict())
    desc = mod.__desc__
    author = mod.__author__
    github_repo = getattr(mod, "__github_repo__", None)
    streamlit_cloud_url = getattr(mod, "__streamlit_cloud_url__", None)
    pypi_name = getattr(mod, "__pypi_name__", None)
    package_name = getattr(mod, "__package_name__", None)
    twitter_username = getattr(mod, "__twitter_username__", None)
    buymeacoffee_username = getattr(mod, "__buymeacoffee_username__", None)
    forum_url = getattr(mod, "__forum_url__", None)
    experimental_playground = getattr(mod, "__experimental_playground__", False)
    experimental_playground_funcs = getattr(mod, "__experimental_playground_funcs__", None)

    extra_title = icon + " " + extra_name.replace("_", " ").title()

    full_doc_path = Path(f"extras/{extra_name}.md")

    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        print(
            EXTRA_MD_TEMPLATE.format(
                extra_title=extra_title,
                extra_name=extra_name,
                extra_author=author,
                description=desc,
            )
        , file=f)


    mkdocs_gen_files.set_edit_path(full_doc_path, "generate.py")
