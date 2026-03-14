# Product Spec Template

Use this template for `work-tmp/<extra_name>-spec.md`.

```markdown
---
author: <github-username>
created: <YYYY-MM-DD>
---

# <Extra Name>

## Summary

<!-- 2-3 sentences describing the extra and its purpose -->

## Problem

<!--
Outline the problem, motivation, or use case.
- Link relevant GitHub issues or user requests
- Describe the pain point this extra solves
-->

## Proposal

### API

<!-- Command name, parameters, types, default values -->

**Simplest usage:**
\```python
from streamlit_extras.<extra_name> import <function_name>

<function_name>()
\```

**Full signature:**
\```python
def <function_name>(
    required_param: str,
    *,
    option: str = "default",
    key: str | None = None,
) -> ReturnType:
    ...
\```

### Behavior

<!--
- What happens on first render?
- What happens on user interaction?
- Error handling and edge cases
- What state is persisted (if any)?
-->

### Design

<!-- Optional: mockups, screenshots, or Figma links -->

### Examples

<!-- Code snippets showing common use cases -->

\```python
import streamlit as st
from streamlit_extras.<extra_name> import <function_name>

# Basic example
result = <function_name>("value")
st.write(result)

# Advanced example with options
result = <function_name>(
    "value",
    option="custom",
    key="my_instance",
)
\```

## Out of Scope

<!-- Features explicitly NOT included in this version -->

- Feature X (future consideration)
- Feature Y (out of scope)

## Checklist

| Item                         | ✅ or comment          |
|------------------------------|------------------------|
| Component type decided       |                        |
| No new heavy dependencies    |                        |
| Works with Streamlit >=1.46  |                        |
| Example function included    |                        |
| Gallery tested               |                        |
```

## API Design Principles

Follow these when designing the API:

1. **Most common use case = fewest arguments** - The simplest usage should require minimal parameters
2. **Sensible defaults** - Every optional parameter should work for 80% of use cases
3. **Start minimal** - You can add parameters later, but never remove them
4. **Use `Literal` over `bool`** - Enables graceful expansion (e.g., `mode: Literal["single", "multi"]` not `multi: bool`)
5. **Limit positional args** - Only 1-3 essential params; rest must be keyword-only (`*,`)
6. **Consistent vocabulary** - Use standard names: `label`, `key`, `help`, `on_change`
