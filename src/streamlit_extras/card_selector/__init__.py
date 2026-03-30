from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Literal, TypedDict, overload

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra

if TYPE_CHECKING:
    from collections.abc import Sequence

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20,400,0,0');

.card-selector-root {
    font-family: var(--st-font, sans-serif);
    color: var(--st-text-color, #333);
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 2px;
}

.card {
    flex: 1 1 0;
    min-width: 120px;
    max-width: 280px;
    padding: 16px;
    border: 1.5px solid var(--st-border-color, #d1d5db);
    border-radius: var(--st-base-radius, 0.5rem);
    background: var(--st-background-color, #fff);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 6px;
    transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
    user-select: none;
    box-sizing: border-box;
}

.card:hover {
    border-color: color-mix(in srgb, var(--st-primary-color, #ff4b4b) 50%, var(--st-border-color, #d1d5db));
    background: color-mix(in srgb, var(--st-primary-color, #ff4b4b) 4%, var(--st-background-color, #fff));
}

.card.selected {
    border-color: var(--st-primary-color, #ff4b4b);
    background: color-mix(in srgb, var(--st-primary-color, #ff4b4b) 8%, var(--st-background-color, #fff));
    box-shadow: 0 0 0 1px var(--st-primary-color, #ff4b4b);
}

.card-icon {
    font-size: 1.5rem;
    line-height: 1;
    flex-shrink: 0;
}

.card-icon .material-symbols-rounded {
    font-family: 'Material Symbols Rounded';
    font-size: 24px;
    font-weight: normal;
    font-style: normal;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-smoothing: antialiased;
    color: var(--st-primary-color, #ff4b4b);
}

.card.selected .card-icon .material-symbols-rounded {
    color: var(--st-primary-color, #ff4b4b);
}

.card:not(.selected) .card-icon .material-symbols-rounded {
    color: var(--st-border-color, #999);
}

.card-title {
    font-size: 0.875rem;
    font-weight: 600;
    line-height: 1.3;
    color: var(--st-text-color, #333);
}

.card-description {
    font-size: 0.8125rem;
    line-height: 1.4;
    color: color-mix(in srgb, var(--st-text-color, #333) 65%, transparent);
}
"""

_JS = """\
export default function(component) {
    const { data, parentElement, setStateValue } = component;
    const items = data?.items ?? [];
    const selected = data?.selected ?? [];
    const selectionMode = data?.selection_mode ?? "single";

    const root = parentElement.querySelector("#card-selector-root");
    if (!root) return () => {};

    root.innerHTML = "";

    const MAT_RE = /^:material\\/(.+):$/;

    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        const card = document.createElement("div");
        card.className = "card";
        if (selected.includes(i)) card.classList.add("selected");

        if (item.icon) {
            const iconEl = document.createElement("div");
            iconEl.className = "card-icon";
            const matMatch = item.icon.match(MAT_RE);
            if (matMatch) {
                const span = document.createElement("span");
                span.className = "material-symbols-rounded";
                span.textContent = matMatch[1];
                iconEl.appendChild(span);
            } else {
                iconEl.textContent = item.icon;
            }
            card.appendChild(iconEl);
        }

        if (item.title) {
            const titleEl = document.createElement("div");
            titleEl.className = "card-title";
            titleEl.textContent = item.title;
            card.appendChild(titleEl);
        }

        if (item.description) {
            const descEl = document.createElement("div");
            descEl.className = "card-description";
            descEl.textContent = item.description;
            card.appendChild(descEl);
        }

        card.addEventListener("click", () => {
            let next;
            if (selectionMode === "multi") {
                if (selected.includes(i)) {
                    next = selected.filter(x => x !== i);
                } else {
                    next = [...selected, i].sort();
                }
            } else {
                next = selected.includes(i) ? [] : [i];
            }
            setStateValue("selected", next);
        });

        root.appendChild(card);
    }

    return () => {};
}
"""

_CARD_SELECTOR_COMPONENT = st.components.v2.component(
    name="streamlit_extras.card_selector",
    html='<div id="card-selector-root" class="card-selector-root"></div>',
    css=_CSS,
    js=_JS,
)


class CardItem(TypedDict, total=False):
    icon: str
    title: str
    description: str


@overload
def card_selector(
    items: Sequence[CardItem],
    *,
    selection_mode: Literal["single"] = ...,
    default: int | None = ...,
    key: str | None = ...,
) -> int | None: ...


@overload
def card_selector(
    items: Sequence[CardItem],
    *,
    selection_mode: Literal["multi"],
    default: list[int] | None = ...,
    key: str | None = ...,
) -> list[int]: ...


@extra
def card_selector(
    items: Sequence[CardItem],
    *,
    selection_mode: Literal["single", "multi"] = "single",
    default: int | list[int] | None = None,
    key: str | None = None,
) -> int | list[int] | None:
    """Display a card-based selector for richer option picking.

    Each option renders as a bordered card with an optional icon, title,
    and description. Like ``st.segmented_control`` but designed for
    choices that need more visual real-estate.

    Args:
        items: Sequence of card items. Each is a dict with optional
            ``icon``, ``title``, and ``description`` string keys.
            Icons support ``:material/name:`` format, emojis, or plain text.
        selection_mode: ``"single"`` (default) allows one selection.
            ``"multi"`` allows toggling multiple cards.
        default: Initially selected index (single mode) or list of
            indices (multi mode). ``None`` means nothing selected.
        key: Unique key for this component instance.

    Returns:
        In single mode: the selected index (``int``) or ``None``.
        In multi mode: a list of selected indices.
    """
    resolved_key = key or "card_selector_default"
    component_state = st.session_state.get(resolved_key, {})

    if "selected" in component_state:
        selected: list[int] = component_state["selected"]
    elif default is not None:
        selected = [default] if isinstance(default, int) else list(default)
    else:
        selected = []

    _CARD_SELECTOR_COMPONENT(
        data={
            "items": [dict(i) for i in items],
            "selected": selected,
            "selection_mode": selection_mode,
        },
        key=resolved_key,
        default={"selected": selected},
        on_selected_change=lambda: None,
    )

    component_state = st.session_state.get(resolved_key, {})
    current: list[int] = component_state.get("selected", selected)

    if selection_mode == "single":
        return current[0] if current else None
    return current


def example_basic() -> None:
    selected = card_selector(
        [
            dict(
                icon=":material/cloud:",
                title="Cloud",
                description="Deploy to a managed cloud service",
            ),
            dict(
                icon=":material/computer:",
                title="Local",
                description="Run on your own machine",
            ),
            dict(
                icon=":material/dns:",
                title="On-Prem",
                description="Host in your data center",
            ),
        ],
        key="demo_basic",
    )
    if selected is not None:
        st.write(f"You picked option **{selected}**")


def example_multi_select() -> None:
    selected = card_selector(
        [
            dict(icon="📊", title="Analytics", description="Usage dashboards"),
            dict(icon="🔔", title="Alerts", description="Email & Slack notifications"),
            dict(icon="🔒", title="Security", description="SSO & audit logs"),
            dict(icon="🚀", title="Performance", description="Caching & CDN"),
        ],
        selection_mode="multi",
        key="demo_multi",
    )
    st.write(f"Selected: **{selected}**")


def example_minimal() -> None:
    selected = card_selector(
        [
            dict(icon=":material/rocket_launch:", title="Starter"),
            dict(icon=":material/star:", title="Pro"),
            dict(icon=":material/diamond:", title="Enterprise"),
        ],
        key="demo_minimal",
    )
    if selected is not None:
        st.write(f"Plan: **{['Starter', 'Pro', 'Enterprise'][selected]}**")


def example_long_text() -> None:
    selected = card_selector(
        [
            dict(
                icon="📊",
                title="Analytics",
                description="Usage dashboards for anything related to what users are using you know.",
            ),
            dict(icon="🔔", title="Alerts", description="Email & Slack notifications"),
            dict(icon="🔒", title="Security", description="SSO & audit logs"),
            dict(icon="🚀", title="Performance", description="Caching & CDN"),
        ],
        selection_mode="multi",
        key="demo_long_text",
    )
    st.write(f"Selected: **{selected}**")


__title__ = "Card Selector"
__desc__ = "Card-based option picker with icons, titles, and descriptions — like st.segmented_control but bigger."
__icon__ = "🃏"
__examples__ = {
    example_basic: [card_selector],
    example_multi_select: [card_selector],
    example_minimal: [card_selector],
    example_long_text: [card_selector],
}
__author__ = "Arnaud Miribel"
__created_at__ = date(2026, 3, 27)
__streamlit_min_version__ = "1.46.0"
