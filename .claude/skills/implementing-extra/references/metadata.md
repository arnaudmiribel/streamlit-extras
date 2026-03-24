# Extra Metadata Attributes

All extras must define these module-level attributes in `__init__.py`.

## Required

| Attribute | Type | Description |
|-----------|------|-------------|
| `__title__` | `str` | Display name shown in gallery |
| `__desc__` | `str` | Short description (1 sentence) |
| `__icon__` | `str` | Single emoji icon |
| `__author__` | `str` | Author name |
| `__examples__` | `list` or `dict` | Example functions for gallery |

## Optional

| Attribute | Type | Description |
|-----------|------|-------------|
| `__streamlit_min_version__` | `str` | Minimum Streamlit version (e.g. `"1.46.0"`) |
| `__playground__` | `bool` | Enable interactive playground in gallery |
| `__tests__` | `list` | Test functions to run |
| `__github_repo__` | `str` | GitHub repository URL |
| `__streamlit_cloud_url__` | `str` | Demo app URL (must contain "streamlit") |
| `__forum_url__` | `str` | Streamlit forum discussion URL |
| `__pypi_name__` | `str` | PyPI package name (requires `__package_name__`) |
| `__package_name__` | `str` | Import name for external package |
| `__twitter_username__` | `str` | Author's Twitter handle |
| `__buymeacoffee_username__` | `str` | Buy Me a Coffee username |

## Auto-populated

| Attribute | Description |
|-----------|-------------|
| `__funcs__` | List of functions decorated with `@extra` |

## Example

```python
from streamlit_extras import extra

@extra
def my_widget(label: str) -> str:
    ...

def example() -> None:
    result = my_widget("Click me")
    st.write(result)

__title__ = "My Widget"
__desc__ = "An interactive widget for user input."
__icon__ = "🎯"
__author__ = "Your Name"
__examples__ = [example]
__streamlit_min_version__ = "1.46.0"
```

## Multiple @extra Functions

If your module has multiple `@extra` decorated functions, use a dict for examples:

```python
@extra
def foo(): ...

@extra
def bar(): ...

def example_foo(): foo()
def example_bar(): bar()

__examples__ = {
    foo: [example_foo],
    bar: [example_bar],
}
```
