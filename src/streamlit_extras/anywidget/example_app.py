"""Example Streamlit app demonstrating the anywidget extra.

Run with: streamlit run example_app.py
Requires: pip install anywidget traitlets drawdata
"""

import streamlit as st

st.set_page_config(page_title="Anywidget Demo", page_icon="🔌", layout="wide")

st.title("🔌 Anywidget Integration Demo")
st.write(
    """
    This demo shows how to use anywidget-compatible widgets in Streamlit
    with full bidirectional interactivity.
    """
)

# Import after page config
from streamlit_extras.anywidget import anywidget

# Check if dependencies are installed
try:
    import anywidget as aw
    import traitlets

    HAS_ANYWIDGET = True
except ImportError:
    HAS_ANYWIDGET = False
    st.error(
        """
        **Missing dependencies!**

        Install anywidget and traitlets:
        ```bash
        pip install anywidget traitlets
        ```
        """
    )
    st.stop()


# Example 1: Counter Widget
st.header("1. Counter Widget")
st.write("A simple counter that demonstrates bidirectional state sync.")


class CounterWidget(aw.AnyWidget):
    _esm = """
    function render({ model, el }) {
      const container = document.createElement("div");
      container.style.cssText = "display: flex; align-items: center; gap: 1rem;";

      const btn = document.createElement("button");
      btn.style.cssText = `
        background: var(--st-primary-color, #ff4b4b);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        cursor: pointer;
        font-family: var(--st-font-family-sans-serif, sans-serif);
        transition: transform 0.1s, opacity 0.2s;
      `;
      btn.onmousedown = () => btn.style.transform = "scale(0.95)";
      btn.onmouseup = () => btn.style.transform = "scale(1)";
      btn.onmouseover = () => btn.style.opacity = "0.9";
      btn.onmouseout = () => { btn.style.opacity = "1"; btn.style.transform = "scale(1)"; };

      const updateBtn = () => {
        btn.innerHTML = `🔢 Count: ${model.get("count")}`;
      };
      updateBtn();

      btn.onclick = () => {
        model.set("count", model.get("count") + 1);
        model.save_changes();
      };

      model.on("change:count", updateBtn);

      container.appendChild(btn);
      el.appendChild(container);
    }
    export default { render };
    """
    count = traitlets.Int(0).tag(sync=True)


if "counter" not in st.session_state:
    st.session_state.counter = CounterWidget()

col1, col2 = st.columns([2, 1])

with col1:
    state = anywidget(st.session_state.counter, key="counter")
    st.write(f"**Python value:** `{state.get('count', 0)}`")

with col2:
    st.write("**Control from Python:**")
    new_val = st.number_input("Set count", value=state.get("count", 0), key="counter_input")
    if st.button("Apply", key="apply_counter"):
        st.session_state.counter.count = new_val
        st.rerun()


# Example 2: Color Picker Widget
st.header("2. Color Picker Widget")
st.write("A custom color picker with live preview.")


class ColorWidget(aw.AnyWidget):
    _esm = """
    function render({ model, el }) {
      const container = document.createElement("div");
      container.style.cssText = "display: flex; align-items: center; gap: 1rem;";

      const picker = document.createElement("input");
      picker.type = "color";
      picker.value = model.get("color") || "#ff4b4b";
      picker.style.cssText = `
        width: 60px;
        height: 40px;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        padding: 0;
      `;

      const preview = document.createElement("div");
      preview.style.cssText = `
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-family: var(--st-font-family-mono, monospace);
        font-size: 1rem;
        color: white;
        background: ${picker.value};
        min-width: 100px;
        text-align: center;
      `;
      preview.textContent = picker.value;

      picker.oninput = () => {
        model.set("color", picker.value);
        model.save_changes();
        preview.style.background = picker.value;
        preview.textContent = picker.value;
      };

      model.on("change:color", () => {
        const newColor = model.get("color");
        picker.value = newColor;
        preview.style.background = newColor;
        preview.textContent = newColor;
      });

      container.appendChild(picker);
      container.appendChild(preview);
      el.appendChild(container);
    }
    export default { render };
    """
    color = traitlets.Unicode("#ff4b4b").tag(sync=True)


if "color_picker" not in st.session_state:
    st.session_state.color_picker = ColorWidget()

state = anywidget(st.session_state.color_picker, key="color")
st.write(f"**Selected color:** `{state.get('color', '#ff4b4b')}`")


# Example 3: Slider Widget
st.header("3. Range Slider Widget")
st.write("A custom range slider with real-time updates.")


class SliderWidget(aw.AnyWidget):
    _esm = """
    function render({ model, el }) {
      const container = document.createElement("div");
      container.style.cssText = "display: flex; flex-direction: column; gap: 0.5rem; width: 100%;";

      const slider = document.createElement("input");
      slider.type = "range";
      slider.min = model.get("min") || 0;
      slider.max = model.get("max") || 100;
      slider.value = model.get("value") || 50;
      slider.style.cssText = `
        width: 100%;
        height: 8px;
        border-radius: 4px;
        cursor: pointer;
        accent-color: var(--st-primary-color, #ff4b4b);
      `;

      const label = document.createElement("div");
      label.style.cssText = `
        font-family: var(--st-font-family-sans-serif, sans-serif);
        font-size: 1rem;
        color: var(--st-text-color, #262730);
      `;
      label.textContent = `Value: ${slider.value}`;

      slider.oninput = () => {
        model.set("value", parseInt(slider.value));
        model.save_changes();
        label.textContent = `Value: ${slider.value}`;
      };

      model.on("change:value", () => {
        slider.value = model.get("value");
        label.textContent = `Value: ${slider.value}`;
      });

      container.appendChild(slider);
      container.appendChild(label);
      el.appendChild(container);
    }
    export default { render };
    """
    value = traitlets.Int(50).tag(sync=True)
    min = traitlets.Int(0).tag(sync=True)
    max = traitlets.Int(100).tag(sync=True)


if "slider" not in st.session_state:
    st.session_state.slider = SliderWidget()

state = anywidget(st.session_state.slider, key="slider")
st.write(f"**Slider value:** `{state.get('value', 50)}`")


# Example 4: External Widget (drawdata)
st.header("4. External Widget (drawdata)")
st.write("Using a pre-built anywidget from PyPI.")

try:
    from drawdata import ScatterWidget

    if "scatter" not in st.session_state:
        st.session_state.scatter = ScatterWidget(width=700, height=400, n_classes=3)

    state = anywidget(st.session_state.scatter, key="scatter")

    col1, col2 = st.columns([2, 1])
    with col1:
        data = state.get("data", [])
        st.write(f"**Data points:** `{len(data)}`")

    with col2:
        if data:
            st.write("**Classes distribution:**")
            colors = [d.get("color", "unknown") for d in data]
            for color in set(colors):
                st.write(f"- {color}: {colors.count(color)}")

    if data and st.checkbox("Show raw data", key="show_data"):
        st.json(data[:10])

except ImportError:
    st.info(
        """
        Install `drawdata` to see this demo:
        ```bash
        pip install drawdata
        ```
        DrawData is a widget for drawing data points that can be used for ML demos.
        """
    )


# Footer
st.divider()
st.write(
    """
    **About anywidget:**
    [anywidget](https://anywidget.dev) is a specification for creating portable
    widget front-ends that work in Jupyter, Colab, VS Code, marimo, and now Streamlit!
    """
)
