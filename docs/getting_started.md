# Getting started

Install the library, then import the extra you want to use in your Streamlit app. Each extra has its own module under `streamlit_extras`.

## Install

You need Python 3.10 or newer and a compatible Streamlit version. Install from PyPI with pip:

```bash
pip install streamlit-extras
```

Or add it to a project managed with uv:

```bash
uv add streamlit-extras
```

## Try your first extra

Create `app.py`:

```python
import streamlit as st
from streamlit_extras.stoggle import stoggle

st.title("My first extra")
stoggle("Show more", "This content appears when you open the toggle.")
```

Run it:

```bash
streamlit run app.py
```

`stoggle` accepts a summary and content string. See its [reference page](extras/stoggle.md) for the source example and function documentation.

## Keep exploring

The [extras catalog](extras/index.md) lists current extras with examples and import paths. If an extra uses a separate PyPI package, its reference page links to that package. Want to add one? Read [Contributing](contributing.md).
