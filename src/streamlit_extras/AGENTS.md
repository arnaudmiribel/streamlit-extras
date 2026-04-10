# Extras Overview

This document provides an overview of all available extras and their implementation approach.

## Component Types

- **pure python**: Pure Python using standard Streamlit API
- **st.html**: Uses [`st.html()`](https://docs.streamlit.io/develop/api-reference/text/st.html) to inject HTML/CSS/JS
- **st.markdown(unsafe_allow_html)**: Uses [`st.markdown()`](https://docs.streamlit.io/develop/api-reference/text/st.markdown) with `unsafe_allow_html=True` to inject markdown with integrated HTML
- **components v1: html**: Uses [`streamlit.components.v1.html()`](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v1.html) to show HTML in an iframe
- **components v1: iframe**: Uses [`streamlit.components.v1.iframe()`](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v1.iframe) to show a URL in an iframe
- **components v2: inline**: Uses [`st.components.v2.component()`](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component) with inline code
- **components v2: static assets**: Uses [`st.components.v2.component()`](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component) with dedicated asset files (e.g. `.js`, `.html`, `.css`) in an `assets/` folder
- **components v2: react**: Uses [`st.components.v2.component()`](https://docs.streamlit.io/develop/tutorials/custom-components/template-react) with a full React frontend

## Choosing a Component Type

Use this guide to select the appropriate implementation approach:

| Requirement | Recommended Type |
|-------------|------------------|
| No UI changes or frontend script execution | **pure python** |
| Requires only HTML and/or CSS | **st.html** |
| Needs to combine markdown with HTML elements | **st.markdown(unsafe_allow_html)** |
| Requires rendering a URL in an iframe | **components v1: iframe** |
| Requires rendering full HTML in an iframe | **components v1: html** |
| Requires JavaScript execution on frontend (no complex UI) | **components v2: inline** |
| Basic UI with pure JS/HTML/CSS | **components v2: inline** (low complexity) or **components v2: static assets** |
| Complex UI requiring React or npm dependencies | **components v2: react** |

## Extras Overview

**Important:** Update this table when adding or modifying extras.

| Extra | Description | Component Type |
|-------|-------------|----------------|
| `add_vertical_space` | Add vertical spacing to your app | pure python |
| `app_logo` | Add a logo on top of the navigation bar | st.html |
| `avatar` | Display a circular avatar image with optional label and caption | components v2: inline |
| `badges` | Create custom badges (PyPI, GitHub, etc.) | st.html |
| `bottom_container` | A container that sticks to the bottom of the app | pure python |
| `buy_me_a_coffee` | Floating button linking to Buy Me a Coffee | components v1: html |
| `card_selector` | Card-based option picker with icons, titles, and descriptions | components v2: inline |
| `capture` | Capture utility extensions for Streamlit | pure python |
| `chart_annotations` | Add annotations to Altair time series charts | pure python |
| `chart_container` | Embed charts in tabs with data exploration | pure python |
| `colored_header` | Create colorful, styled headers | st.html |
| `concurrency_limiter` | Limit function execution concurrency | pure python |
| `cookie_manager` | Read/write browser cookies from Python | components v2: inline |
| `diagrams` | Render architecture diagrams with SVG output | components v2: inline |
| `customize_running` | Customize the running widget appearance | st.html |
| `dataframe_explorer` | Interactive dataframe filtering UI | pure python |
| `echo_expander` | Show executed code in an expander | pure python |
| `eval_javascript` | Evaluate JavaScript in browser, return to Python | components v2: inline |
| `exception_handler` | Override Streamlit's uncaught exception handler | pure python |
| `floating_button` | A button fixed at bottom right corner | st.html |
| `function_explorer` | Generate UI for any Python function | pure python |
| `great_tables` | Render Great Tables objects in Streamlit | st.html |
| `grid` | Place elements on a specified grid layout | pure python |
| `image_compare_slider` | Compare two images with an interactive slider overlay | components v2: react |
| `image_selector` | Select images from a gallery | pure python |
| `json_editor` | Interactive JSON viewer/editor built with React | components v2: react |
| `jupyterlite` | Add a Jupyterlite sandbox to your app | components v1: iframe |
| `keyboard_text` | Create keyboard-styled text | st.html |
| `keyboard_url` | Keyboard shortcuts that open URLs | st.markdown(unsafe_allow_html) |
| `let_it_rain` | Create emoji rain animations | st.html |
| `mandatory_date_range` | Date range picker requiring both dates | pure python |
| `pagination` | Pagination widget with prev/next arrows and page numbers | components v2: react |
| `mention` | Create Notion-style mention links with icons | st.html |
| `metric_cards` | Restyle metrics as styled cards | st.html |
| `radial_menu` | Circular menu around a central button | components v2: static assets |
| `redirect` | Programmatically redirect users to external or internal URLs | components v2: inline |
| `resizable_columns` | Drag-to-resize columns, a drop-in replacement for st.columns | components v2: react |
| `row` | Place elements in a horizontal row | pure python |
| `sandbox` | Execute untrusted Streamlit code safely | components v1: html |
| `scroll_to_element` | Programmatically scroll to any element by its key | components v2: inline |
| `sigma_graph` | Interactive network graph visualization using sigma.js | components v2: react |
| `skeleton` | Display skeleton placeholder while loading | pure python |
| `star_rating` | Read-only star rating display | st.html |
| `stateful_button` | Toggle button that keeps track of its state | pure python |
| `steps` | Progress-steps indicator for multi-step workflows | components v2: inline |
| `stateful_chat` | Chat container with automatic history tracking | pure python |
| `stodo` | Create simple to-do items | st.markdown(unsafe_allow_html) |
| `stoggle` | Notion-style toggle button | st.html |
| `stylable_container` | Container with custom CSS styling | pure python |
| `tags` | Display GitHub-style tags | st.html |
| `three_viewer` | 3D model viewer using Three.js | components v2: react |
| `word_importances` | Highlight words based on importance scores | st.html |

## Development Tips

- Prefer `st.html` over `st.markdown(unsafe_allow_html=True)`. Only use `st.markdown` with `unsafe_allow_html` when you need both markdown rendering and HTML in the same content.
- When working on **components v2** extras, use the `/building-streamlit-custom-components-v2` skill for guidance on the v2 component API, state management, and theming.

## Building React-based CCv2 Components

For **components v2: react** extras, the frontend is built with React/TypeScript and Vite.

### Current React Extras

- `pagination/` - Pagination widget (recommended reference for new React extras)
- `json_editor/` - Interactive JSON viewer/editor

### Creating a React Extra

Use the `pagination/` extra as a reference implementation. Copy its structure and adapt:

1. Copy the `pagination/` directory to `src/streamlit_extras/<extra_name>/`
2. Rename files and update references to your extra name
3. Update `frontend/package.json` with your extra's name
4. Implement your React component in `frontend/src/`
5. Update the Python wrapper in `__init__.py`
6. Add standard extra metadata (`__title__`, `__icon__`, etc.)
7. Register in `src/streamlit_extras/pyproject.toml` (see Registration below)

### Directory Structure

```
src/streamlit_extras/
  pyproject.toml             # Shared CCv2 manifest (auto-generated during build)
  <extra_name>/
    __init__.py              # Python wrapper with @extra decorator
    frontend/
      package.json           # npm dependencies
      tsconfig.json          # TypeScript config
      vite.config.ts         # Vite build config
      src/
        index.tsx            # React root / FrontendRenderer
        <Component>.tsx      # React component
      build/                 # Built assets (generated during uv build)
        index-<hash>.js
```

### Build Process

1. Run `uv build` to build the wheel - frontends are compiled automatically via `scripts/hatch_build.py`
2. The hook auto-detects extras with `frontend/package.json`
3. Built assets are generated during build (not committed to repo)
4. The wheel includes only the compiled JS bundles, not frontend source

**For development:** Build manually:
```bash
cd src/streamlit_extras/<extra_name>/frontend
npm install
npm run build     # Production build
npm run dev       # Watch mode for development
```

The `npm run dev` command watches for changes to your frontend code and rebuilds automatically. When you make changes, refresh your Streamlit app to see them.

### Registration

React-based CCv2 components must be registered in `src/streamlit_extras/pyproject.toml`:

```toml
[[tool.streamlit.component.components]]
name = "your_extra_name"
asset_dir = "your_extra_name/frontend/build"
```

### Key Files

- **`src/streamlit_extras/pyproject.toml`**: Shared CCv2 manifest for all React-based components (auto-generated during build)
- **`__init__.py`**: Uses `st.components.v2.component()` with `js="index-*.js"` glob
- **`frontend/src/index.tsx`**: Implements `FrontendRenderer` interface, manages React roots
- **`frontend/src/<Component>.tsx`**: React component using `setStateValue()` for state

### Theming

Use CSS custom properties for Streamlit theme integration (e.g. `var(--st-primary-color)`). See the [Theming and styling guide](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/theming) for all available variables.

### References

**Concepts:**
- [Quick start examples](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/examples)
- [Component registration](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/register)
- [Mounting components](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/mount)
- [State vs trigger values](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/state-and-triggers)
- [Bidirectional communication](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/communicate)
- [Theming and styling](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/theming)
- [Package-based components](https://docs.streamlit.io/develop/concepts/custom-components/components-v2/package-based)

**API Reference (Python):**
- [`st.components.v2.component`](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component)
- [`ComponentRenderer`](https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.types.componentrenderer)

**API Reference (Frontend):**
- [`FrontendRendererArgs`](https://docs.streamlit.io/develop/api-reference/custom-components/component-v2-lib-frontendrendererargs)
- [`FrontendRenderer`](https://docs.streamlit.io/develop/api-reference/custom-components/component-v2-lib-frontendrenderer)
- [`FrontendState`](https://docs.streamlit.io/develop/api-reference/custom-components/component-v2-lib-frontendstate)
- [`CleanupFunction`](https://docs.streamlit.io/develop/api-reference/custom-components/component-v2-lib-cleanupfunction)
