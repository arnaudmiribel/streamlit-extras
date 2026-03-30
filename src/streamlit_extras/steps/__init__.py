from __future__ import annotations

from contextlib import AbstractContextManager, contextmanager
from typing import TYPE_CHECKING, Literal

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20,400,0,0');

:host {
    overflow: hidden;
}

.stepper-root {
    font-family: var(--st-font, sans-serif);
    color: var(--st-text-color, #333);
}

/* ---- vertical ---- */

.stepper-vertical {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.stepper-vertical .step {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    min-height: 40px;
}

.stepper-vertical .step-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 40px;
    flex-shrink: 0;
}

.step-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8125rem;
    font-weight: 600;
    flex-shrink: 0;
    box-sizing: border-box;
    line-height: 1;
    transition: background 0.2s, border-color 0.2s, color 0.2s;
}

.step-icon .material-symbols-rounded {
    font-family: 'Material Symbols Rounded';
    font-size: 20px;
    font-weight: normal;
    font-style: normal;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-smoothing: antialiased;
}

.stepper-vertical .step-tail {
    width: 2px;
    flex: 1;
    min-height: 8px;
    transition: background 0.2s;
}

.stepper-vertical .step:last-child .step-tail {
    visibility: hidden;
}

.stepper-vertical .step-label {
    padding: 2px 0 12px 12px;
    font-size: 0.875rem;
    line-height: 32px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: color 0.2s, font-weight 0.2s;
}

/* ---- horizontal ---- */

.stepper-horizontal {
    display: flex;
    flex-direction: column;
    width: 100%;
}

.stepper-horizontal .step-track {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 100%;
}

.stepper-horizontal .step-segment {
    display: flex;
    align-items: center;
    flex: 1;
}

.stepper-horizontal .step-segment:first-child .step-line-before,
.stepper-horizontal .step-segment:last-child .step-line-after {
    display: none;
}

.stepper-horizontal .step-labels .step-label:first-child {
    text-align: left;
    padding-left: 0;
}

.stepper-horizontal .step-labels .step-label:last-child {
    text-align: right;
    padding-right: 0;
}

.stepper-horizontal .step-line-before,
.stepper-horizontal .step-line-after {
    flex: 1;
    height: 2px;
    transition: background 0.2s;
}



.stepper-horizontal .step-labels {
    display: flex;
    flex-direction: row;
    width: 100%;
}

.stepper-horizontal .step-label {
    flex: 1;
    margin-top: 6px;
    font-size: 0.8125rem;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 4px;
    transition: color 0.2s, font-weight 0.2s;
}

/* ---- state colors (applied via JS using CSS vars) ---- */

.step-icon.completed {
    background: var(--st-primary-color, #ff4b4b);
    color: #fff;
    border: 2px solid var(--st-primary-color, #ff4b4b);
}

.step-icon.active {
    background: var(--st-background-color, #fff);
    color: var(--st-primary-color, #ff4b4b);
    border: 2px solid var(--st-primary-color, #ff4b4b);
}

.step-icon.inactive {
    background: var(--st-background-color, #fff);
    color: var(--st-border-color, #ccc);
    border: 2px solid var(--st-border-color, #ccc);
}

.step-tail.completed,
.step-line-before.completed,
.step-line-after.completed {
    background: var(--st-primary-color, #ff4b4b);
}

.step-tail.incomplete,
.step-line-before.incomplete,
.step-line-after.incomplete {
    background: var(--st-border-color, #d1d5db);
}

.step-label.completed {
    color: var(--st-text-color, #333);
}

.step-label.active {
    color: var(--st-text-color, #333);
    font-weight: 600;
}

.step-label.inactive {
    color: var(--st-border-color, #aaa);
}
"""

_JS = """\
export default function(component) {
    const { data, parentElement } = component;
    const labels = data?.labels ?? [];
    const current = data?.current ?? 0;
    const horizontal = data?.horizontal ?? false;
    const orientation = horizontal ? "horizontal" : "vertical";
    const icons = data?.icons ?? null;

    const root = parentElement.querySelector("#stepper-root");
    if (!root) return () => {};

    root.innerHTML = "";
    root.className = "stepper-root stepper-" + orientation;

    const total = labels.length;

    const MAT_RE = /^:material\\/(.+):$/;

    function setIconContent(el, value, state) {
        if (value == null) {
            if (state === "completed") {
                const span = document.createElement("span");
                span.className = "material-symbols-rounded";
                span.textContent = "check";
                el.appendChild(span);
            } else if (state === "active") {
                const inner = document.createElement("div");
                inner.style.width = "10px";
                inner.style.height = "10px";
                inner.style.borderRadius = "50%";
                inner.style.background = "var(--st-primary-color, #ff4b4b)";
                el.appendChild(inner);
            }
            return;
        }
        const matMatch = String(value).match(MAT_RE);
        if (matMatch) {
            const span = document.createElement("span");
            span.className = "material-symbols-rounded";
            span.textContent = matMatch[1];
            el.appendChild(span);
        } else {
            el.textContent = String(value);
        }
    }

    function makeIcon(index) {
        const icon = document.createElement("div");
        icon.className = "step-icon";
        const value = icons ? icons[index] : null;
        if (index < current) {
            icon.classList.add("completed");
            if (value != null) {
                setIconContent(icon, value, "completed");
            } else {
                setIconContent(icon, null, "completed");
            }
        } else if (index === current) {
            icon.classList.add("active");
            setIconContent(icon, value, "active");
        } else {
            icon.classList.add("inactive");
            setIconContent(icon, value, "inactive");
        }
        return icon;
    }

    if (orientation === "vertical") {
        for (let i = 0; i < total; i++) {
            const step = document.createElement("div");
            step.className = "step";

            const indicator = document.createElement("div");
            indicator.className = "step-indicator";

            indicator.appendChild(makeIcon(i));

            const tail = document.createElement("div");
            tail.className = "step-tail " + (i < current ? "completed" : "incomplete");
            indicator.appendChild(tail);

            step.appendChild(indicator);

            const label = document.createElement("div");
            label.className = "step-label";
            label.textContent = labels[i] || "";
            if (i < current) label.classList.add("completed");
            else if (i === current) label.classList.add("active");
            else label.classList.add("inactive");

            step.appendChild(label);
            root.appendChild(step);
        }
    } else {
        const track = document.createElement("div");
        track.className = "step-track";

        const labelsRow = document.createElement("div");
        labelsRow.className = "step-labels";

        for (let i = 0; i < total; i++) {
            const segment = document.createElement("div");
            segment.className = "step-segment";

            const lineBefore = document.createElement("div");
            lineBefore.className = "step-line-before " + (i <= current ? "completed" : "incomplete");
            segment.appendChild(lineBefore);

            segment.appendChild(makeIcon(i));

            const lineAfter = document.createElement("div");
            lineAfter.className = "step-line-after " + (i < current ? "completed" : "incomplete");
            segment.appendChild(lineAfter);

            track.appendChild(segment);

            const label = document.createElement("div");
            label.className = "step-label";
            label.textContent = labels[i] || "";
            if (i < current) label.classList.add("completed");
            else if (i === current) label.classList.add("active");
            else label.classList.add("inactive");
            labelsRow.appendChild(label);
        }

        root.appendChild(track);
        root.appendChild(labelsRow);
    }

    return () => {};
}
"""

_STEPS_COMPONENT = st.components.v2.component(
    name="streamlit_extras.steps",
    html='<div id="stepper-root"></div>',
    css=_CSS,
    js=_JS,
)

_STATE_KEY_PREFIX = "_steps_state_"


@contextmanager
def _step_context(*, visible: bool) -> Generator[None]:
    if visible:
        yield
    else:
        empty = st.empty()
        with empty.container():
            yield
        empty.empty()


class StepsState:
    """Return value of :func:`steps`.

    Provides context managers for each step via indexing (``steps[i]``)
    and navigation helpers that update the internal step counter and
    call :func:`st.rerun`.
    """

    def __init__(self, *, n_steps: int, current: int, session_key: str) -> None:
        self._n_steps = n_steps
        self._current = current
        self._session_key = session_key
        self._contexts = [_step_context(visible=(i == current)) for i in range(n_steps)]

    @property
    def current(self) -> int:
        return self._current

    def __getitem__(self, index: int) -> AbstractContextManager[None]:
        return self._contexts[index]

    def __len__(self) -> int:
        return self._n_steps

    def _go(self, step: int) -> None:
        clamped = max(0, min(step, self._n_steps - 1))
        st.session_state[self._session_key] = clamped
        st.rerun()

    def next(self) -> None:
        """Advance to the next step and rerun."""
        self._go(self._current + 1)

    def previous(self) -> None:
        """Go back to the previous step and rerun."""
        self._go(self._current - 1)

    def set(self, step: int) -> None:
        """Jump to a specific step (zero-based) and rerun."""
        self._go(step)

    def reset(self) -> None:
        """Return to the first step and rerun."""
        self._go(0)


@extra
def steps(
    labels: Sequence[str],
    *,
    current: int = 0,
    icons: Sequence[str | int] | None = None,
    horizontal: bool = False,
    height: int | None = None,
    width: Literal["stretch", "content"] = "stretch",
    key: str | None = None,
) -> StepsState:
    """Display a progress-steps indicator and return a :class:`StepsState`.

    Renders a visual steps (progress indicator) and returns a
    :class:`StepsState` object. Index it to get context managers for
    each step, or call its navigation methods (``.next()``,
    ``.previous()``, ``.set(n)``, ``.reset()``) to change the active
    step and rerun.

    Inspired by `Base Web ProgressSteps <https://baseweb.design/components/progress-steps/>`_.

    Args:
        labels: Step titles (one per step).
        current: Initial/default step index (zero-based). Once the user
            navigates via the returned object's methods, the internally
            persisted value takes precedence.
        icons: Optional sequence of icons for each step. Accepts
            integers (displayed as numbers), emoji strings, or
            Material Symbols in ``":material/icon_name:"`` format.
            When ``None`` (default), dots are shown with a checkmark
            for completed steps.
        horizontal: If ``True``, lay out steps horizontally.
            Defaults to ``False`` (vertical).
        height: Component height in pixels. Defaults to an auto-computed
            value based on the number of steps and orientation.
        width: ``"stretch"`` (default) fills the container. ``"content"``
            sizes to fit the content.
        key: Unique key for this component instance. Required when using
            navigation methods (``.next()``, etc.) or when placing
            multiple steps components.

    Returns:
        A :class:`StepsState` object. Use ``steps[i]`` as a context
        manager to place content for step *i*. Call ``steps.next()``,
        ``steps.previous()``, ``steps.set(n)``, or ``steps.reset()``
        to navigate.

    Example:
        >>> s = steps(["Step 1", "Step 2"], key="s")
        >>> with s[0]:
        ...     if st.button("Next"):
        ...         s.next()
        >>> with s[1]:
        ...     st.write("Done!")
    """
    session_key = _STATE_KEY_PREFIX + (key or "default")

    if session_key in st.session_state:
        active = st.session_state[session_key]
    else:
        active = current
        st.session_state[session_key] = active

    active = max(0, min(active, len(labels) - 1))

    computed_height = (64 if horizontal else 8 + 48 * len(labels)) if height is None else height

    _STEPS_COMPONENT(
        data={
            "labels": list(labels),
            "current": active,
            "horizontal": horizontal,
            "icons": [str(i) for i in icons] if icons is not None else None,
        },
        key=key,
        height=computed_height,
        width=width,
    )

    return StepsState(
        n_steps=len(labels),
        current=active,
        session_key=session_key,
    )


def example_vertical_numbered() -> None:

    left, right = st.columns((1, 3))

    with left:
        s = steps(
            ["Account Setup", "Preferences", "Confirmation"],
            icons=range(1, 4),
            key="demo_vn",
        )

    with right:
        with s[0]:
            st.text_input("Your name", key="name_input")
            if st.button("Next", key="vn_next_0"):
                s.next()

        with s[1]:
            st.selectbox("Theme", ["Light", "Dark"], key="theme_select")
            with st.container(horizontal=True):
                if st.button("Back", key="vn_back_1"):
                    s.previous()
                if st.button("Next", key="vn_next_1"):
                    s.next()

        with s[2]:
            st.success("All done! You're all set.")
            if st.button("Reset", key="vn_reset"):
                s.reset()


def example_horizontal_numbered() -> None:
    h_steps = steps(
        ["Upload", "Review", "Submit"],
        horizontal=True,
        icons=range(1, 4),
        key="demo_hn",
    )

    with h_steps[0]:
        st.info("Upload your files here.")
        if st.button("Next", key="hn_next_0"):
            h_steps.next()

    with h_steps[1]:
        st.info("Review your submission.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Back", key="hn_back_1"):
                h_steps.previous()
        with c2:
            if st.button("Next", key="hn_next_1"):
                h_steps.next()

    with h_steps[2]:
        st.info("Click submit to finish.")
        if st.button("Start over", key="hn_reset"):
            h_steps.reset()


def example_vertical_dots() -> None:
    s = steps(
        ["Connect", "Configure", "Deploy", "Monitor"],
        key="demo_vd",
    )

    with s[0]:
        st.write("Connect to your data source.")
        if st.button("Next", key="vd_next_0"):
            s.next()

    with s[1]:
        st.write("Set up your pipeline configuration.")
        if st.button("Next", key="vd_next_1"):
            s.next()

    with s[2]:
        st.write("Deploy to production.")
        if st.button("Next", key="vd_next_2"):
            s.next()

    with s[3]:
        st.write("Monitor your deployment.")
        if st.button("Reset", key="vd_reset"):
            s.reset()


def example_material_icons() -> None:
    _labels = ["Cart", "Shipping", "Payment", "Done"]
    h_steps = steps(
        _labels,
        horizontal=True,
        icons=[
            ":material/shopping_cart:",
            ":material/local_shipping:",
            ":material/payment:",
            ":material/check_circle:",
        ],
        key="demo_hd",
    )

    with h_steps[0]:
        st.write("Review your cart items.")
        if st.button("Next", key="hd_next_0"):
            h_steps.next()

    with h_steps[1]:
        st.write("Enter shipping details.")
        if st.button("Next", key="hd_next_1"):
            h_steps.next()

    with h_steps[2]:
        st.write("Complete payment.")
        if st.button("Next", key="hd_next_2"):
            h_steps.next()

    with h_steps[3]:
        st.balloons()
        st.success("Order placed!")
        if st.button("New order", key="hd_reset"):
            h_steps.reset()


def example_emoji_icons() -> None:
    s = steps(
        ["Idea", "Build", "Test", "Ship"],
        icons=["💡", "🔨", "🧪", "🚀"],
        key="demo_emoji",
    )

    with s[0]:
        st.write("Brainstorm your idea.")
        if st.button("Next", key="em_next_0"):
            s.next()

    with s[1]:
        st.write("Build the prototype.")
        if st.button("Next", key="em_next_1"):
            s.next()

    with s[2]:
        st.write("Run your tests.")
        if st.button("Next", key="em_next_2"):
            s.next()

    with s[3]:
        st.success("Shipped!")
        if st.button("Start over", key="em_reset"):
            s.reset()


def example_jump_to_step() -> None:
    s = steps(
        ["Intro", "Details", "Review", "Submit"],
        icons=range(1, 5),
        key="demo_jump",
    )

    with s[0]:
        st.write("Welcome! Jump to any step:")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Go to Details", key="j_1"):
                s.set(1)
        with c2:
            if st.button("Go to Review", key="j_2"):
                s.set(2)
        with c3:
            if st.button("Go to Submit", key="j_3"):
                s.set(3)

    with s[1]:
        st.write("Fill in your details.")
        if st.button("Back", key="j_back_1"):
            s.previous()

    with s[2]:
        st.write("Review everything.")
        if st.button("Back", key="j_back_2"):
            s.previous()

    with s[3]:
        st.write("Ready to submit!")
        if st.button("Reset", key="j_reset"):
            s.reset()


__title__ = "Steps"
__desc__ = "Progress-steps indicator for multi-step workflows, with vertical/horizontal orientation and numbered or dotted styles."
__icon__ = "🪜"
__examples__ = {
    example_vertical_numbered: [steps],
    example_horizontal_numbered: [steps],
    example_vertical_dots: [steps],
    example_material_icons: [steps],
    example_emoji_icons: [steps],
    example_jump_to_step: [steps],
}
__author__ = "Arnaud Miribel"
