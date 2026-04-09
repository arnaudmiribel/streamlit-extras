"""Anywidget integration for Streamlit.

Render any anywidget-compatible widget in Streamlit with full bidirectional interactivity.
Supports inline ESM, file-based ESM, pre-bundled widgets, and CDN imports.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra

if TYPE_CHECKING:
    import anywidget as aw


def _get_esm_content(widget: aw.AnyWidget) -> str:
    """Extract ESM content from widget (handles string or Path)."""
    esm = getattr(widget, "_esm", None)
    if esm is None:
        msg = f"Widget {widget.__class__.__name__} must have an _esm attribute"
        raise ValueError(msg)
    if isinstance(esm, Path):
        return esm.read_text()
    if callable(esm):
        return esm()
    return str(esm)


def _get_css_content(widget: aw.AnyWidget) -> str | None:
    """Extract CSS content from widget (handles string or Path)."""
    css = getattr(widget, "_css", None)
    if css is None:
        return None
    if isinstance(css, Path):
        return css.read_text()
    if callable(css):
        return css()
    return str(css)


def _extract_synced_traits(widget: aw.AnyWidget) -> dict[str, Any]:
    """Extract traits marked with sync=True."""
    synced: dict[str, Any] = {}
    for name, trait in widget.traits().items():
        # Skip private traits and known internal traits
        if name.startswith("_") or name in ("comm", "keys", "log", "layout"):
            continue
        # Only include traits marked with sync=True
        if not trait.metadata.get("sync", False):
            continue
        try:
            value = getattr(widget, name)
            # Verify the value is JSON serializable
            json.dumps({name: value})
            synced[name] = value
        except (TypeError, OverflowError):
            # Skip non-serializable traits silently
            pass
    return synced


@cache
def _get_component() -> Any:
    """Lazily initialize the CCv2 component.

    Returns:
        The component callable.
    """
    return streamlit.components.v2.component(
        "streamlit-extras.anywidget",
        html='<div class="react-root"></div>',
        js="index-*.js",
    )


def _noop() -> None:
    """No-op callback for CC v2 state changes."""


def _get_message_key(key: str | None) -> str:
    """Get the session state key for storing messages."""
    return f"_anywidget_messages_{key or 'default'}"


def _get_msg_counter_key(key: str | None) -> str:
    """Get the session state key for message counter."""
    return f"_anywidget_msg_counter_{key or 'default'}"


def _get_widget_state_key(key: str | None) -> str:
    """Get the session state key for tracking widget state."""
    return f"_anywidget_widget_state_{key or 'default'}"


@extra
def anywidget(
    widget: aw.AnyWidget,
    *,
    key: str | None = None,
    height: int | None = None,
    on_message: Any | None = None,
) -> dict[str, Any]:
    """Render an anywidget-compatible widget in Streamlit.

    This function wraps any widget that follows the anywidget specification,
    enabling full bidirectional interactivity between Python and JavaScript.

    Supported widget types:
    - Inline ESM widgets (``_esm = "..."```)
    - File-based ESM widgets (``_esm = Path("widget.js")``)
    - Pre-bundled widgets (like drawdata, ipywidgets-based widgets)
    - Widgets with CDN imports

    Args:
        widget: An anywidget-compatible widget instance. Must have an ``_esm``
            attribute containing the ESM module code or path.
        key: Unique key for the widget instance. Required when using multiple
            instances of the same widget type.
        height: Optional fixed height in pixels. If not specified, the widget
            will auto-size based on its content.
        on_message: Optional callback function to handle custom messages from
            the widget's JavaScript code (via ``model.send()``). The callback
            receives the message content as its argument.

    Returns:
        A dictionary containing the current values of all synced traits.
        The values update bidirectionally when either Python or JavaScript
        modifies them.

    Example:
        >>> import anywidget
        >>> import traitlets
        >>>
        >>> class CounterWidget(anywidget.AnyWidget):
        ...     _esm = '''
        ...     function render({ model, el }) {
        ...       let btn = document.createElement("button");
        ...       btn.innerHTML = `count is ${model.get("count")}`;
        ...       btn.onclick = () => {
        ...         model.set("count", model.get("count") + 1);
        ...         model.save_changes();
        ...       };
        ...       model.on("change:count", () => {
        ...         btn.innerHTML = `count is ${model.get("count")}`;
        ...       });
        ...       el.appendChild(btn);
        ...     }
        ...     export default { render };
        ...     '''
        ...     count = traitlets.Int(0).tag(sync=True)
        >>>
        >>> widget = CounterWidget()
        >>> state = anywidget(widget, key="counter")
        >>> st.write(f"Count: {state['count']}")
    """
    # Extract widget content
    esm_content = _get_esm_content(widget)
    css_content = _get_css_content(widget)

    # Get the current trait values from the widget instance
    widget_traits = _extract_synced_traits(widget)

    # Get stored widget state (widget values after last result update)
    # This allows us to detect when Python code explicitly changed a trait
    widget_state_key = _get_widget_state_key(key)
    widget_state_after_last_result = st.session_state.get(widget_state_key, None)

    # Determine which traits to send to the frontend
    # Only send traits that Python explicitly changed (widget value != stored value)
    # This prevents overwriting JS-side changes on every rerun
    traits_to_send: dict[str, Any] = {}
    if widget_state_after_last_result is None:
        # First render: send all traits
        traits_to_send.update(dict(widget_traits.items()))
    else:
        # Subsequent renders: only send traits that Python changed
        for name, widget_value in widget_traits.items():
            stored_value = widget_state_after_last_result.get(name)
            if widget_value != stored_value:
                # Python changed this trait, send it
                traits_to_send[name] = widget_value

    # Create no-op callbacks for each trait (CC v2 callbacks don't receive values)
    callbacks: dict[str, Any] = {}
    for name in widget_traits:
        callbacks[f"on_{name}_change"] = _noop

    # Add callback for custom messages from JS
    callbacks["on__anywidget_msg_change"] = _noop

    # Build default traits (used by CC v2 for initial state)
    default_traits = dict(widget_traits)
    default_traits["_anywidget_msg"] = None

    # If no user traits, we need at least one state field for the component
    # Use a dummy "_initialized" state
    if len(widget_traits) == 0:
        default_traits["_initialized"] = True
        traits_to_send["_initialized"] = True
        callbacks["on__initialized_change"] = _noop

    # Get the component
    component = _get_component()

    # Build component kwargs
    component_kwargs: dict[str, Any] = {
        "key": key,
        "data": {
            "esm": esm_content,
            "css": css_content,
            "traits": traits_to_send,
        },
        "default": default_traits,
        **callbacks,
    }

    if height is not None:
        component_kwargs["height"] = height

    # Call the component
    result = component(**component_kwargs)

    # Process custom messages from JS
    if result and on_message is not None:
        msg = result.get("_anywidget_msg")
        if msg is not None and isinstance(msg, dict):
            msg_key = _get_message_key(key)
            last_msg_id = st.session_state.get(msg_key, 0)
            current_msg_id = msg.get("id", 0)
            if current_msg_id > last_msg_id:
                st.session_state[msg_key] = current_msg_id
                # Call the message handler
                try:
                    on_message(msg.get("content"))
                except Exception as e:
                    st.error(f"Error in message handler: {e}")

    # Update the widget instance with values from the result (JS → Python sync)
    if result:
        for name in widget_traits:
            if name in result:
                current_value = getattr(widget, name, None)
                new_value = result[name]
                if current_value != new_value:
                    setattr(widget, name, new_value)

    # Store widget state AFTER updating from result
    # This is used to detect Python-side changes on the next rerun
    st.session_state[widget_state_key] = _extract_synced_traits(widget)

    # Filter out internal fields from result
    if result:
        result = {k: v for k, v in result.items() if not k.startswith("_anywidget_")}

    # Return the result or default values (without internal fields)
    if result:
        return result
    return {k: v for k, v in default_traits.items() if not k.startswith("_")}


# Example widgets for demo
_COUNTER_ESM = """
function render({ model, el }) {
  // Create styled button
  const btn = document.createElement("button");
  btn.style.cssText = `
    background: var(--st-primary-color, #ff4b4b);
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    cursor: pointer;
    font-family: var(--st-font-family-sans-serif, sans-serif);
    transition: opacity 0.2s;
  `;
  btn.onmouseover = () => btn.style.opacity = "0.8";
  btn.onmouseout = () => btn.style.opacity = "1";

  // Update button text
  const updateBtn = () => {
    btn.innerHTML = `Count: ${model.get("count")}`;
  };
  updateBtn();

  // Handle click
  btn.onclick = () => {
    model.set("count", model.get("count") + 1);
    model.save_changes();
  };

  // Listen for changes from Python
  model.on("change:count", updateBtn);

  el.appendChild(btn);
}
export default { render };
"""


def example_counter() -> None:
    """Interactive counter widget demo."""
    st.write("### Counter Widget")
    st.write("Click the button to increment the count. The value syncs bidirectionally with Python.")

    try:
        import anywidget as aw
        import traitlets
    except ImportError:
        st.error("Install `anywidget` and `traitlets` to run this example: `pip install anywidget traitlets`")
        return

    class CounterWidget(aw.AnyWidget):
        _esm = _COUNTER_ESM
        count = traitlets.Int(0).tag(sync=True)

    if "counter_widget" not in st.session_state:
        st.session_state.counter_widget = CounterWidget()

    widget = st.session_state.counter_widget
    state = anywidget(widget, key="counter_demo")

    st.write(f"**Python sees count:** `{state.get('count', 0)}`")

    # Demo Python-to-JS update
    if st.button("Reset from Python", key="reset_counter"):
        widget.count = 0
        st.rerun()


_TEXT_INPUT_ESM = """
function render({ model, el }) {
  // Create container
  const container = document.createElement("div");
  container.style.cssText = "display: flex; flex-direction: column; gap: 0.5rem;";

  // Create input
  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type here...";
  input.style.cssText = `
    padding: 0.5rem;
    border: 1px solid var(--st-gray-30, #d3d3d3);
    border-radius: 0.5rem;
    font-size: 1rem;
    font-family: var(--st-font-family-sans-serif, sans-serif);
    outline: none;
  `;
  input.onfocus = () => input.style.borderColor = "var(--st-primary-color, #ff4b4b)";
  input.onblur = () => input.style.borderColor = "var(--st-gray-30, #d3d3d3)";

  // Set initial value
  input.value = model.get("text") || "";

  // Handle input changes
  input.oninput = () => {
    model.set("text", input.value);
    model.save_changes();
  };

  // Listen for changes from Python
  model.on("change:text", () => {
    if (input.value !== model.get("text")) {
      input.value = model.get("text") || "";
    }
  });

  container.appendChild(input);
  el.appendChild(container);
}
export default { render };
"""


def example_text_input() -> None:
    """Text input widget with bidirectional binding."""
    st.write("### Text Input Widget")
    st.write("Type in the input below. The value syncs instantly with Python.")

    try:
        import anywidget as aw
        import traitlets
    except ImportError:
        st.error("Install `anywidget` and `traitlets` to run this example: `pip install anywidget traitlets`")
        return

    class TextWidget(aw.AnyWidget):
        _esm = _TEXT_INPUT_ESM
        text = traitlets.Unicode("Hello, Streamlit!").tag(sync=True)

    if "text_widget" not in st.session_state:
        st.session_state.text_widget = TextWidget()

    widget = st.session_state.text_widget
    state = anywidget(widget, key="text_demo")

    st.write(f"**Python sees text:** `{state.get('text', '')}`")
    st.write(f"**Character count:** `{len(state.get('text', ''))}`")


def example_external_widget() -> None:
    """Using a pre-built anywidget (drawdata)."""
    st.write("### External Widget (drawdata)")
    st.write("Draw data points on the scatter plot. Data syncs to Python in real-time.")

    try:
        from drawdata import ScatterWidget
    except ImportError:
        st.info(
            "Install `drawdata` to see this demo: `pip install drawdata`\n\n"
            "DrawData is a widget for drawing data points that can be used for ML demos."
        )
        return

    if "scatter_widget" not in st.session_state:
        st.session_state.scatter_widget = ScatterWidget(width=600, height=400)

    widget = st.session_state.scatter_widget
    state = anywidget(widget, key="scatter_demo", height=420)

    data = state.get("data", [])
    st.write(f"**Data points drawn:** `{len(data)}`")

    if data:
        st.write("**Sample data:**")
        st.json(data[:3])


__title__ = "Anywidget"
__desc__ = "Render any anywidget-compatible widget in Streamlit with full bidirectional interactivity."
__icon__ = "🔌"
__examples__ = [
    example_counter,
    example_text_input,
    example_external_widget,
]
__author__ = "Lukas Masuch"
__streamlit_min_version__ = "1.46.0"
