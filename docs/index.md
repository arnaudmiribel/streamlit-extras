---
title: Home
hide:
  - toc
---

<div class="extras-hero" markdown="1">

# Small additions. Better apps.

Streamlit extras are focused Python utilities and UI components that fit into your app. Find the one you need, copy its import, and keep building.

[Get started](getting_started.md){ .md-button .md-button--primary } [Browse extras](extras/index.md){ .md-button }

</div>

<div class="extras-paths" markdown="1">

<div class="extras-path" markdown="1">

### Install and try

Add `streamlit-extras` to your environment and try a working example in minutes.

[Installation and first app →](getting_started.md)

</div>

<div class="extras-path" markdown="1">

### Find the right extra

Browse generated reference pages with imports, function documentation, and example code.

[Explore the catalog →](extras/index.md)

</div>

<div class="extras-path" markdown="1">

### Share what you built

Contribute a reusable, self-contained extra with a working gallery example.

[Contribution guide →](contributing.md)

</div>

</div>

## See it in an app

A toggle is one example of an extra you can drop into an existing Streamlit script:

```python
import streamlit as st
from streamlit_extras.stoggle import stoggle

st.title("A little more context")
stoggle("How does this work?", "Click to reveal the answer.")
```

Run the script with `streamlit run app.py`. See the [toggle reference](extras/stoggle.md) for its arguments and more examples.

## Built to feel at home in Streamlit

Extras cover small layout helpers, Python utilities, and interactive components. Each has its own import path and documented example, so you can choose only what your app needs. The [catalog](extras/index.md) is the best place to discover what's available now.

Want to help another builder? Start with the [contribution guide](contributing.md) or the [agent-friendly project guide](agents.md).
