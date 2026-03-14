---
name: implementing-extra
description: Guides implementation of new streamlit-extras from spec to verification. Use when adding a new extra, creating a Streamlit component, or when the user says "implement extra", "new extra", or "add extra".
license: Apache-2.0
---

# Implementing a New Extra

Multi-step workflow for adding new extras to streamlit-extras. Always read and follow `src/streamlit_extras/AGENTS.md` first.

## Workflow Checklist

Copy this checklist and track progress:

```
Implementation Progress:
- [ ] Step 1: Write product spec in work-tmp/
- [ ] Step 2: Decide component type
- [ ] Step 3: Implement the extra
- [ ] Step 4: Verify implementation
```

## Step 1: Write Product Spec

Create a spec in `work-tmp/<extra_name>-spec.md` before coding.

**Spec structure:**

```markdown
# <Extra Name> Spec

## Problem
Why does this extra need to exist? Link to user requests or pain points.

## API Design

### Simplest Usage
\```python
from streamlit_extras.<extra_name> import <function_name>
<function_name>()  # minimal args
\```

### Full API
\```python
def <function_name>(
    required_param: str,  # Essential params first
    *,
    common_option: str = "default",  # Common options (keyword-only)
    advanced_option: bool = False,  # Advanced options last
    key: str | None = None,
) -> ReturnType:
    ...
\```

## Behavior
- What happens on first render?
- What happens on user interaction?
- What state is persisted?

## Out of Scope
- Features explicitly NOT included in v1
```

**API design principles** (from Streamlit guidelines):
- Most common use case = fewest arguments
- Sensible defaults for 80% of cases
- Start minimal (you can add params later, never remove)
- Use `Literal` types over booleans for future expansion
- Only 1-3 positional params; rest keyword-only

## Step 2: Decide Component Type

Read the decision table in `src/streamlit_extras/AGENTS.md` under "Choosing a Component Type".

Quick reference:

| Requirement | Type |
|-------------|------|
| No UI/frontend needed | **pure python** |
| HTML/CSS only | **st.html** |
| Markdown + HTML | **st.markdown(unsafe_allow_html)** |
| URL in iframe | **components v1: iframe** |
| Full HTML in iframe | **components v1: html** |
| JavaScript execution (simple) | **components v2: inline** |
| Basic JS/HTML/CSS UI | **components v2: inline** or **static assets** |
| Complex UI / React / npm deps | **components v2: react** |

For CCv2 components, use the `/building-streamlit-custom-components-v2` skill.

## Step 3: Implement

Create `src/streamlit_extras/<extra_name>/__init__.py` with:

1. **Main function** decorated with `@extra`
2. **Example function** for the gallery
3. **Required metadata** (see [references/metadata.md](references/metadata.md))

**Template:**

```python
from streamlit_extras import extra

@extra
def my_extra(param: str, *, key: str | None = None) -> None:
    """One-line description.

    Args:
        param: Description.
        key: Unique key for this instance.
    """
    ...

def example() -> None:
    """Example for gallery."""
    my_extra("demo")

__title__ = "My Extra"
__desc__ = "Short description of what it does."
__icon__ = "..."  # Single emoji
__author__ = "Your Name"
__examples__ = [example]
__streamlit_min_version__ = "1.46.0"  # If using recent features
```

## Step 4: Verify

Run these checks before committing:

```bash
# Linting and formatting
uv run ruff check --fix src/streamlit_extras/<extra_name>/
uv run ruff format src/streamlit_extras/<extra_name>/

# Type checking
uv run mypy src/streamlit_extras/<extra_name>/

# Tests (validates metadata)
uv run pytest tests/test_extras.py -k <extra_name>

# Gallery test
uv run streamlit run gallery/streamlit_app.py
```

**For CCv2 React components**, also verify the build:

```bash
# Build wheel (compiles React frontends via hatch hook)
uv build

# Check build artifacts exist
ls src/streamlit_extras/<extra_name>/frontend/build/
```

## References

- **Metadata attributes**: [references/metadata.md](references/metadata.md)
- **CCv2 components**: Use `/building-streamlit-custom-components-v2` skill
- **Extras overview**: `src/streamlit_extras/AGENTS.md`
