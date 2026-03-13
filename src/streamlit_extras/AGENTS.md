# Extras Overview

This document provides an overview of all available extras and their implementation approach.

**Important:** Update this table when adding or modifying extras.

## Component Types

- **pure python**: Pure Python using standard Streamlit API
- **st.html**: Uses `st.html()` to inject HTML/CSS/JS
- **st.markdown(unsafe_allow_html)**: Uses `st.markdown()` with `unsafe_allow_html=True` to inject markdown with integrated HTML
- **components v1: html**: Uses `streamlit.components.v1.html()` to show HTML in an iframe
- **components v1: iframe**: Uses `streamlit.components.v1.iframe()` to show a URL in an iframe
- **components v2: inline**: Uses `st.components.v2.component()` with inline code
- **components v2: static assets**: Uses `st.components.v2.component()` with dedicated asset files (e.g. `.js`, `.html`, `.css`)

## Extras Table

| Extra | Description | Component Type |
|-------|-------------|----------------|
| `add_vertical_space` | Add vertical spacing to your app | pure python |
| `app_logo` | Add a logo on top of the navigation bar | st.html |
| `badges` | Create custom badges (PyPI, GitHub, etc.) | st.html |
| `bottom_container` | A container that sticks to the bottom of the app | pure python |
| `buy_me_a_coffee` | Floating button linking to Buy Me a Coffee | components v1: html |
| `capture` | Capture utility extensions for Streamlit | pure python |
| `chart_annotations` | Add annotations to Altair time series charts | pure python |
| `chart_container` | Embed charts in tabs with data exploration | pure python |
| `colored_header` | Create colorful, styled headers | st.html |
| `concurrency_limiter` | Limit function execution concurrency | pure python |
| `cookie_manager` | Read/write browser cookies from Python | components v2: inline |
| `customize_running` | Customize the running widget appearance | st.html |
| `dataframe_explorer` | Interactive dataframe filtering UI | pure python |
| `echo_expander` | Show executed code in an expander | pure python |
| `eval_javascript` | Evaluate JavaScript in browser, return to Python | components v2: inline |
| `exception_handler` | Override Streamlit's uncaught exception handler | pure python |
| `floating_button` | A button fixed at bottom right corner | st.html |
| `function_explorer` | Generate UI for any Python function | pure python |
| `great_tables` | Render Great Tables objects in Streamlit | st.html |
| `grid` | Place elements on a specified grid layout | pure python |
| `image_selector` | Select images from a gallery | pure python |
| `jupyterlite` | Add a Jupyterlite sandbox to your app | components v1: iframe |
| `keyboard_text` | Create keyboard-styled text | st.html |
| `keyboard_url` | Keyboard shortcuts that open URLs | st.markdown(unsafe_allow_html) |
| `let_it_rain` | Create emoji rain animations | st.html |
| `mandatory_date_range` | Date range picker requiring both dates | pure python |
| `mention` | Create Notion-style mention links with icons | st.html |
| `metric_cards` | Restyle metrics as styled cards | st.html |
| `radial_menu` | Circular menu around a central button | components v2: static assets |
| `row` | Place elements in a horizontal row | pure python |
| `sandbox` | Execute untrusted Streamlit code safely | components v1: html |
| `skeleton` | Display skeleton placeholder while loading | pure python |
| `star_rating` | Read-only star rating display | st.html |
| `stateful_button` | Toggle button that keeps track of its state | pure python |
| `stateful_chat` | Chat container with automatic history tracking | pure python |
| `stodo` | Create simple to-do items | st.markdown(unsafe_allow_html) |
| `stoggle` | Notion-style toggle button | st.html |
| `stylable_container` | Container with custom CSS styling | pure python |
| `tags` | Display GitHub-style tags | st.html |
| `word_importances` | Highlight words based on importance scores | st.html |

## Component Type Summary

| Component Type | Count |
|----------------|-------|
| pure python | 18 |
| st.html | 14 |
| st.markdown(unsafe_allow_html) | 2 |
| components v1: html | 2 |
| components v1: iframe | 1 |
| components v2: inline | 2 |
| components v2: static assets | 1 |
