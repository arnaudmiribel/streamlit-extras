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

Use the template in [references/spec-template.md](references/spec-template.md) which follows Streamlit's product spec format:

1. **Summary** - 2-3 sentences describing the extra
2. **Problem** - Motivation, user requests, pain points
3. **Proposal** - API design, behavior, examples
4. **Out of Scope** - Features not included in v1

Follow the Streamlit API design principles from: https://raw.githubusercontent.com/streamlit/streamlit/refs/heads/develop/specs/AGENTS.md

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
```

## Step 4: Verify

Run these checks before committing:

```bash
# Linting and formatting
uv run ruff check --fix
uv run ruff format

# Type checking
uv run mypy
uv run ty check

# Tests (validates metadata)
uv run pytest
```

**For CCv2 React components**, also verify the build:

```bash
# Build wheel (compiles React frontends via hatch hook)
uv build

# Check build artifacts exist
ls src/streamlit_extras/<extra_name>/frontend/build/
```

## References

- **Spec template**: [references/spec-template.md](references/spec-template.md)
- **Metadata attributes**: [references/metadata.md](references/metadata.md)
- **API design principles**: https://raw.githubusercontent.com/streamlit/streamlit/refs/heads/develop/specs/AGENTS.md
- **CCv2 components**: Use `/building-streamlit-custom-components-v2` skill
- **Extras overview**: `src/streamlit_extras/AGENTS.md`
