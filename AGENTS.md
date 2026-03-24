# AGENTS.md

Rules and context for AI coding agents working on streamlit-extras.

## Project Overview

**streamlit-extras** is a community-driven collection of useful Streamlit components and utilities ("extras") that extend Streamlit's functionality. Each extra is a self-contained module providing widgets, layouts, or utilities not yet in core Streamlit.

**Mission:** Make it easy to discover, share, and use community Streamlit components.

## Repository Structure

- `src/streamlit_extras/`: Main package where all extras live
  - `__init__.py`: The `@extra` decorator (registers functions)
  - `<extra_name>/`: Each extra is its own directory with an `__init__.py`
- `gallery/`: Demo Streamlit app showcasing all extras
- `tests/`: Pytest tests (validates extra metadata)
- `docs/`: MkDocs documentation source
- `pyproject.toml`: Dependencies, ruff/mypy config
- `scripts/hatch_build.py`: Build hook that auto-compiles React frontends
- `work-tmp/`: Temporary files, specs, and scripts (gitignored)

## Essential Commands

**Setup:**
- `uv sync`: Install Python dependencies
- `cd src/streamlit_extras/<extra>/frontend && npm install`: Install npm deps for React extras

**Development:**
- `uv run streamlit run gallery/streamlit_app.py`: Run demo app
- `cd src/streamlit_extras/<extra>/frontend && npm run dev`: Watch mode for React extras

**Building:**
- `uv build`: Build wheel (auto-compiles React frontends via hatch hook)

**Quality checks:**
- `uv run pytest`: Run tests
- `uv run ruff check --fix`: Lint + autofix
- `uv run ruff format`: Format code
- `uv run mypy`: Type check
- `uv run ty check`: Alternative type checker

**Pre-commit (runs all checks):**
- `pre-commit install`: Setup hooks
- `pre-commit run --all-files`: Run manually

## Tech Stack

- **Python 3.10+** with **uv** for dependency management
- **Streamlit** (>=1.54.0) as the core framework
- **Node.js** (>=18 LTS) with npm for React-based extras
- **Ruff** for linting and formatting
- **mypy** + **ty** for type checking
- **pytest** for testing
- **MkDocs** for documentation

## Creating a New Extra

1. Create `src/streamlit_extras/<extra_name>/__init__.py`
2. Use the `@extra` decorator on your main function
3. Add required metadata attributes (see table below)
4. Run `uv run pytest` to validate metadata
5. Test in gallery: `uv run streamlit run gallery/streamlit_app.py`

### Metadata Attributes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `__title__` | Yes | `str` | Display name of the extra |
| `__desc__` | Yes | `str` | Short description of what it does |
| `__icon__` | Yes | `str` | Emoji icon for the extra |
| `__author__` | Yes | `str` | Author name |
| `__examples__` | Yes | `list` or `dict` | Example functions (dict if multiple `@extra` funcs) |
| `__funcs__` | Auto | `list` | Auto-populated by `@extra` decorator |
| `__playground__` | No | `bool` | Enable playground in gallery |
| `__tests__` | No | `list` | Test functions to run |
| `__github_repo__` | No | `str` | GitHub repository URL |
| `__streamlit_cloud_url__` | No | `str` | Demo app URL (must contain "streamlit") |
| `__forum_url__` | No | `str` | Streamlit forum discussion URL |
| `__experimental_playground__` | No | `bool` | Enable experimental playground |
| `__experimental_playground_funcs__` | No | `list` | Functions for experimental playground |
| `__inputs__` | No | `dict` | Playground input config |
| `__pypi_name__` | No | `str` | PyPI package name (requires `__package_name__`) |
| `__package_name__` | No | `str` | Import name for external package |
| `__twitter_username__` | No | `str` | Author's Twitter handle |
| `__buymeacoffee_username__` | No | `str` | Buy Me a Coffee username |

### Example

```python
from .. import extra

@extra
def my_function():
    ...

def example():
    my_function()

__title__ = "My Extra"
__desc__ = "What it does"
__icon__ = "🎯"
__author__ = "Your Name"
__examples__ = [example]
```

## React-Based Extras (CCv2)

Some extras use React frontends via Streamlit's Custom Components v2 (CCv2) API. These require Node.js (>=18 LTS) and npm to build.

For detailed CCv2 documentation (directory structure, build process, registration, theming), see `src/streamlit_extras/AGENTS.md`.

**Quick commands:**
- `cd src/streamlit_extras/<extra>/frontend && npm install && npm run build` - Build frontend
- `cd src/streamlit_extras/<extra>/frontend && npm run dev` - Watch mode for development
- `uv build` - Build wheel (auto-compiles all React frontends via hatch hook)

## Code Style

- Follow existing patterns in the codebase
- Use type hints on all functions (`disallow_untyped_defs` is enabled)
- Keep extras self-contained in their own directories
- Escape user input in HTML components (`html.escape()` for XSS prevention)

## Testing

Tests in `tests/test_extras.py` automatically validate all extras have:
- Required metadata (`__title__`, `__icon__`, `__desc__`, `__author__`)
- At least one example function
- Functions registered via `@extra` decorator

Run `uv run pytest -v` to see per-extra test results.
