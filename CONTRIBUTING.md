# Contributing

Have a small Streamlit improvement that others could reuse? Contributions can be a new Python function, a UI component, or an integration with an existing package. Keep the extra focused, self-contained, and easy to try.

## Choose an approach

Use Streamlit's Python API for behavior that doesn't need custom frontend code. For markup and styles, prefer `st.html`; escape user-provided text with `html.escape`. For interactive frontend code, look at the existing [component approaches](https://arnaudmiribel.github.io/streamlit-extras/components/) and the repository's [CCv2 guidance](https://github.com/arnaudmiribel/streamlit-extras/blob/main/src/streamlit_extras/AGENTS.md). Avoid adding frontend complexity when the built-in Streamlit API will do.

## Add an extra

1. Create `src/streamlit_extras/<name>/__init__.py`. Give your public function type hints and register it with `@extra` from `streamlit_extras`.
2. Set `__title__`, `__desc__`, `__icon__`, `__author__`, and `__examples__`. Make the example runnable in the gallery. If there are multiple registered functions, `__examples__` must map examples to the functions they use.
3. If you wrap an existing PyPI package, include `__pypi_name__` and `__package_name__`, and declare its dependency in `pyproject.toml`.
4. Run the gallery and checks below. Open a pull request explaining the user-facing behavior, with a screenshot or short recording when the UI changes.

Here is a minimal starting point:

```python
from .. import extra


@extra
def greeting(name: str) -> None:
    import streamlit as st

    st.write(f"Hello, {name}!")


def example() -> None:
    greeting("Streamlit")


__title__ = "Greeting"
__desc__ = "Show a friendly greeting."
__icon__ = "👋"
__author__ = "Your name"
__examples__ = [example]
```

## Try it locally

From the repository root:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run streamlit run gallery/streamlit_app.py
```

For a React-based extra, build its frontend with `npm install && npm run build` from its `frontend/` directory. A wheel build (`uv build`) compiles React frontends and packages their built assets.

For an existing-package integration, add its dependency to `pyproject.toml`. For agent-assisted work, see the [project guide](https://arnaudmiribel.github.io/streamlit-extras/agents/); review and test generated code before submitting.
