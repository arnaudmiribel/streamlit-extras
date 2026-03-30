"""
specialized_inputs — a streamlit-extras component
==================================================

Polished, specialized text inputs built on ``st.components.v2`` that look and
feel exactly like native Streamlit widgets.

Design principles (matching native ``st.text_input`` precisely):
- Input background  → ``--st-secondary-background-color`` (gray pill)
- Prefix/suffix bg  → slightly darker (``--st-border-color`` tint)
- Border            → none at rest; thin ``--st-primary-color`` line on focus,
                      NO glow/box-shadow (matches Streamlit exactly)
- Label             → normal weight (not bold), same as native
- Icon              → inside-input SVG adornments (in the prefix/suffix area)
                      inherit ``currentColor``; no icon is prefixed in the label
- Help tooltip      → ``help`` parameter, rendered as a right-aligned (?) icon
                      with a hover tooltip (component-rendered)
- Dark mode         → uses only ``--st-*`` CSS vars, adapts automatically

Public API (mirrors ``st.text_input``)
---------------------------------------
    specialized_text_input(label, value="", *, placeholder="",
                           key=None, on_change=None, args=None, kwargs=None,
                           disabled=False, label_visibility="visible",
                           icon=None, prefix=None, suffix=None,
                           help=None, error=None)

Convenience wrappers:
    phone_input, email_input, url_input, money_input,
    search_input, password_input

Requirements: streamlit >= 1.45
"""

from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING, Any, Literal

import streamlit as st
from streamlit.components.v2 import component

from .. import extra

if TYPE_CHECKING:
    from collections.abc import Callable

# ---------------------------------------------------------------------------
# Inline SVG adornment icons (used only INSIDE the input for prefix/suffix
# area icons; the label has no prefixed icon)
# 20x20 viewport, filled, inherits currentColor.
# ---------------------------------------------------------------------------
_ADORNMENT_ICONS: dict[str, str] = {
    "phone": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.01-.24 '
        "11.47 11.47 0 0 0 3.58.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 "
        '1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.58a1 1 0 0 1-.25 1.01z"/>'
        "</svg>"
    ),
    "mail": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 '
        '0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z"/>'
        "</svg>"
    ),
    "language": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 '
        "12S17.52 2 11.99 2zm6.93 6h-2.95a15.65 15.65 0 0 0-1.38-3.56A8.03 8.03 0 0 "
        "1 18.92 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 "
        "1.91-3.96zM4.26 14C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 "
        "1.32-.14 2s.06 1.34.14 2H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.987 "
        "7.987 0 0 1 5.08 16zm2.95-8H5.08a7.987 7.987 0 0 1 4.33-3.56A15.65 15.65 0 "
        "0 0 8.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 "
        "2.76-1.91 3.96zM14.34 14H9.66c-.09-.66-.16-1.32-.16-2s.07-1.35.16-2h4.68c"
        ".09.65.16 1.32.16 2s-.07 1.34-.16 2zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56"
        "h2.95a8.03 8.03 0 0 1-4.33 3.56zM16.36 14c.08-.66.14-1.32.14-2s-.06-1.34-"
        '.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2h-3.38z"/>'
        "</svg>"
    ),
    "search": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 '
        "9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 "
        '0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>'
        "</svg>"
    ),
    "lock": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10'
        "c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2"
        "s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 "
        '3.1 1.39 3.1 3.1v2z"/>'
        "</svg>"
    ),
    "visibility": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 '
        "11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 "
        '2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>'
        "</svg>"
    ),
    "visibility_off": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-'
        "1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 "
        "2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46A11.804 11.804 0 0 0 1 "
        "12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 "
        "3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 "
        ".22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 "
        '0-.79.2-1.53.53-2.2zm4.31-.78 3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>'
        "</svg>"
    ),
    "alternate_email": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10h5v-2h-5c-4.34 0-8-3.66-8-'
        "8s3.66-8 8-8 8 3.66 8 8v1.43c0 .79-.71 1.57-1.5 1.57s-1.5-.78-1.5-1.57V12"
        "c0-2.76-2.24-5-5-5s-5 2.24-5 5 2.24 5 5 5c1.38 0 2.64-.56 3.54-1.47.65.89 "
        "1.77 1.47 2.96 1.47C19.44 19 21 17.43 21 15.43V12c0-5.52-4.48-10-10-10zm0 "
        '13c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/>'
        "</svg>"
    ),
}

# ---------------------------------------------------------------------------
# CSS — matches native st.text_input exactly:
#   • secondaryBackgroundColor for the whole widget body
#   • no border at rest, thin primaryColor border on focus (no shadow)
#   • label: normal weight, small, native text color
#   • prefix/suffix: slightly darker bg (border-color tint), separated by a
#     1 px internal divider
#   • error state: red border (always visible, thin, 1 px)
# ---------------------------------------------------------------------------
_COMPONENT_CSS = r"""
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Root container ─────────────────────────────────────────────────────── */
.si-root {
    font-family: var(--st-font, sans-serif);
    font-size: var(--st-base-font-size, 14px);
    color: var(--st-text-color, #31333f);
    width: 100%;
    /* Give a tiny top clearance so focus border isn't clipped */
    padding-top: 1px;
    padding-bottom: 1px;
}

/* ── Label row (label + optional help icon) ─────────────────────────────── */
.si-label-row {
    display: flex;
    align-items: center;
    gap: 0.3em;
    margin-bottom: 0.15rem;
    min-height: 1.4em;
}
.si-label {
    flex: 1 1 auto;
    min-width: 0;
    font-size: 0.875em;
    font-weight: 400;              /* ← NOT bold, matching native Streamlit */
    color: var(--st-text-color, #31333f);
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.si-label-row.hidden   { visibility: hidden; }
.si-label-row.collapsed { display: none; }

/* ── Help tooltip trigger ───────────────────────────────────────────────── */
.si-help {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-left: auto;
    color: var(--st-gray-color, #9ea3b0);
    cursor: help;
    flex-shrink: 0;
    position: relative;
}
.si-help svg { display: block; }
.si-help-bubble {
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    right: 0;
    left: auto;
    transform: none;

    /* Native-like tooltip: light surface, dark text */
    background: var(--st-background-color, #fff);
    color: var(--st-text-color, #31333f);

    font-size: 0.85em;
    line-height: 1.2;
    padding: 0.45em 0.65em;
    border-radius: 10px;
    border: 1px solid color-mix(in srgb, var(--st-text-color, #31333f) 10%, transparent);

    /* Native tooltip is compact and mostly single-line */
    max-width: 240px;
    white-space: nowrap;

    pointer-events: none;
    z-index: 9999;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
}
.si-help:hover .si-help-bubble { display: block; }

/* ── Input wrapper ──────────────────────────────────────────────────────── */
.si-wrapper {
    display: flex;
    align-items: stretch;
    /* Native Streamlit: secondaryBackgroundColor for the widget body */
    background: var(--st-secondary-background-color, #f0f2f6);
    border-radius: var(--st-base-radius, 0.5rem);
    /* No border at rest — exactly like native Streamlit default */
    border: 1px solid transparent;
    transition: border-color 0.1s ease;
    overflow: hidden;
    min-height: 2.4rem;
}

/* Focus: thin primary color border, NO box-shadow/glow */
.si-wrapper:focus-within {
    border-color: var(--st-primary-color, #ff4b4b);
}

/* Error: thin red border (always visible) */
.si-wrapper.si-has-error {
    border-color: var(--st-red-color, #bd2f2f);
}

/* Disabled */
.si-wrapper.si-disabled {
    opacity: 0.55;
    cursor: not-allowed;
}

/* ── Leading / trailing adornments ─────────────────────────────────────── */
.si-adornment {
    display: none;                 /* hidden unless populated */
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    padding: 0 0.5rem;
    color: var(--st-gray-color, #9ea3b0);
    user-select: none;
    background: transparent;
    line-height: 1;
}
.si-adornment.si-visible { display: flex; }

/* Prefix / suffix text badge — slightly darker background */
.si-adornment.si-prefix-text {
    padding: 0 0.5rem 0 0.65rem;
    font-size: 0.85em;
    color: var(--st-text-color, #31333f);
    /* Closer to st.chat_input: a subtle text-color tint over secondary bg */
    background: var(
        --st-chat-input-background-color,
        color-mix(in srgb, var(--st-text-color, #31333f) 8%, var(--st-secondary-background-color, #f0f2f6) 92%)
    );
    white-space: nowrap;
}
.si-adornment.si-suffix-text {
    padding: 0 0.65rem 0 0.5rem;
    font-size: 0.85em;
    color: var(--st-text-color, #31333f);
    background: var(
        --st-chat-input-background-color,
        color-mix(in srgb, var(--st-text-color, #31333f) 8%, var(--st-secondary-background-color, #f0f2f6) 92%)
    );
    white-space: nowrap;
}

/* Icon-only adornment (leading icon inside the field) */
.si-adornment.si-icon-adornment {
    width: 2.4rem;
    min-width: 2.4rem;
    padding: 0;
    color: var(--st-gray-color, #9ea3b0);
}

/* Password toggle button */
.si-adornment.si-btn {
    cursor: pointer;
    padding: 0 0.55rem;
    color: var(--st-gray-color, #9ea3b0);
    transition: color 0.1s ease;
    border-radius: 0 var(--st-base-radius, 0.5rem) var(--st-base-radius, 0.5rem) 0;
}
.si-adornment.si-btn:hover {
    color: var(--st-primary-color, #ff4b4b);
}
.si-adornment svg { display: block; }

/* ── The <input> ────────────────────────────────────────────────────────── */
.si-input {
    flex: 1 1 auto;
    min-width: 0;
    border: none;
    outline: none;
    background: transparent;
    font-family: inherit;
    font-size: inherit;
    color: var(--st-text-color, #31333f);
    padding: 0 0.65rem;
    min-height: 2.4rem;
    line-height: 1;
    caret-color: var(--st-primary-color, #ff4b4b);
}
.si-input::placeholder {
    /* Match st.chat_input placeholder tint (muted text, not "gray") */
    color: var(
        --st-secondary-text-color,
        color-mix(in srgb, var(--st-text-color, #31333f) 45%, transparent)
    );
    opacity: 1;
}
.si-input:disabled { cursor: not-allowed; }
/* Kill browser chrome */
.si-input::-ms-reveal, .si-input::-ms-clear { display: none; }
.si-input::-webkit-search-decoration,
.si-input::-webkit-search-cancel-button,
.si-input::-webkit-inner-spin-button,
.si-input::-webkit-outer-spin-button { -webkit-appearance: none; display: none; }
.si-input[type=number] { -moz-appearance: textfield; }

/* ── Error message (inline, below the field) ────────────────────────────── */
.si-error-msg {
    display: none;
    margin-top: 0.25rem;
    font-size: 0.8em;
    line-height: 1.4;
    color: var(--st-red-text-color, #bd2f2f);
}
.si-error-msg.si-visible { display: block; }
"""

# JS: append a child div, never touch parentElement.innerHTML (would wipe CCv2's <style>)
_COMPONENT_JS = r"""
export default function (component) {
    const { data, setStateValue, parentElement } = component;

    /* ── Build DOM once ─────────────────────────────────────────────── */
    let root = parentElement.querySelector('.si-root');
    if (!root) {
        root = document.createElement('div');
        root.className = 'si-root';

        // Label row
        const labelRow = document.createElement('div');
        labelRow.id = 'si-label-row';
        labelRow.className = 'si-label-row';

        const labelEl = document.createElement('span');
        labelEl.id = 'si-label';
        labelEl.className = 'si-label';

        const helpEl = document.createElement('span');
        helpEl.id = 'si-help';
        helpEl.className = 'si-help';
        // Help icon SVG: match native outline style
        helpEl.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg><span class="si-help-bubble" id="si-help-bubble"></span>`;

        labelRow.appendChild(labelEl);
        labelRow.appendChild(helpEl);

        // Wrapper
        const wrapper = document.createElement('div');
        wrapper.id = 'si-wrapper';
        wrapper.className = 'si-wrapper';

        const leading = document.createElement('span');
        leading.id = 'si-leading';
        leading.className = 'si-adornment';

        const input = document.createElement('input');
        input.id = 'si-input';
        input.className = 'si-input';
        input.setAttribute('autocomplete', 'off');
        input.setAttribute('spellcheck', 'false');

        const trailing = document.createElement('span');
        trailing.id = 'si-trailing';
        trailing.className = 'si-adornment';

        wrapper.appendChild(leading);
        wrapper.appendChild(input);
        wrapper.appendChild(trailing);

        // Error message
        const errorMsg = document.createElement('div');
        errorMsg.id = 'si-error-msg';
        errorMsg.className = 'si-error-msg';

        root.appendChild(labelRow);
        root.appendChild(wrapper);
        root.appendChild(errorMsg);
        parentElement.appendChild(root);
    }

    const labelRow  = root.querySelector('#si-label-row');
    const labelEl   = root.querySelector('#si-label');
    const helpEl    = root.querySelector('#si-help');
    const helpBubble= root.querySelector('#si-help-bubble');
    const wrapper   = root.querySelector('#si-wrapper');
    const leading   = root.querySelector('#si-leading');
    let   input     = root.querySelector('#si-input');
    const trailing  = root.querySelector('#si-trailing');
    const errorMsg  = root.querySelector('#si-error-msg');

    /* ── Label ──────────────────────────────────────────────────────── */
    const vis = data.label_visibility ?? 'visible';
    labelEl.textContent = data.label ?? '';
    labelRow.className = 'si-label-row ' + vis;

    /* ── Help tooltip ───────────────────────────────────────────────── */
    if (data.help) {
        helpBubble.textContent = data.help;
        helpEl.style.display = 'inline-flex';
    } else {
        helpEl.style.display = 'none';
    }

    /* ── Flags ──────────────────────────────────────────────────────── */
    const disabled = !!data.disabled;
    const hasError = !!(data.error);
    wrapper.classList.toggle('si-disabled', disabled);
    wrapper.classList.toggle('si-has-error', hasError);

    /* ── Input type / value ─────────────────────────────────────────── */
    const baseType = data.input_type ?? 'text';
    if (input.dataset.baseType !== baseType) {
        input.type = baseType;
        input.dataset.baseType = baseType;
    }
    input.disabled    = disabled;
    input.placeholder = data.placeholder ?? '';
    const incoming = String(data.value ?? '');
    if (input.value !== incoming) input.value = incoming;


    /* ── Leading adornment ──────────────────────────────────────────── */
    leading.innerHTML = '';
    leading.className = 'si-adornment';
    if (data.icon_svg) {
        leading.innerHTML = data.icon_svg;
        leading.classList.add('si-visible', 'si-icon-adornment');
    } else if (data.prefix) {
        leading.textContent = data.prefix;
        leading.classList.add('si-visible', 'si-prefix-text');
        // When there's a prefix badge, remove padding-left from input
        input.style.paddingLeft = '0.4rem';
    } else {
        input.style.paddingLeft = '';
    }

    /* ── Trailing adornment ─────────────────────────────────────────── */
    trailing.className = 'si-adornment';
    trailing.innerHTML = '';

    if (data.is_password) {
        // Password toggle — init listener only once
        trailing.classList.add('si-visible', 'si-btn');
        trailing.title = 'Toggle visibility';

        // Keep latest state on the element so the one-time handler can use it.
        trailing._pwdDisabled = disabled;
        trailing._pwdIconVis = data.icon_visibility;
        trailing._pwdIconVisOff = data.icon_visibility_off;

        trailing._getPwdInput = () => root.querySelector('#si-input');

        const renderEye = () => {
            const inp = trailing._getPwdInput?.();
            if (!inp) return;
            trailing.innerHTML = inp.type === 'text'
                ? trailing._pwdIconVisOff
                : trailing._pwdIconVis;
        };
        trailing._renderEye = renderEye;
        renderEye();

        if (!trailing._pwdInit) {
            trailing._pwdInit = true;

            // Prevent the click from blurring the input (blur triggers setStateValue → rerun).
            trailing.addEventListener('pointerdown', (e) => e.preventDefault());

            trailing.addEventListener('click', () => {
                if (trailing._pwdDisabled) return;
                const inp = trailing._getPwdInput?.();
                if (!inp) return;

                const start = inp.selectionStart;
                const end = inp.selectionEnd;

                inp.type = inp.type === 'password' ? 'text' : (inp.dataset.baseType || 'password');
                trailing._renderEye?.();

                inp.focus();
                if (start !== null && end !== null) {
                    try {
                        inp.setSelectionRange(start, end);
                    } catch {
                        // Some browsers disallow restoring selection after type toggle.
                    }
                }
            });
        }
    } else if (data.suffix) {
        trailing.textContent = data.suffix;
        trailing.classList.add('si-visible', 'si-suffix-text');
        input.style.paddingRight = '0.4rem';
    } else if (data.trailing_icon_svg) {
        trailing.innerHTML = data.trailing_icon_svg;
        trailing.classList.add('si-visible', 'si-icon-adornment');
    } else {
        input.style.paddingRight = '';
    }

    /* ── Error message ──────────────────────────────────────────────── */
    if (hasError && typeof data.error === 'string') {
        errorMsg.textContent = data.error;
        errorMsg.classList.add('si-visible');
    } else {
        errorMsg.textContent = '';
        errorMsg.classList.remove('si-visible');
    }

    /* ── Event wiring ───────────────────────────────────────────────── */
    input.onblur = () => setStateValue('value', input.value);
    input.onkeydown = (e) => { if (e.key === 'Enter') setStateValue('value', input.value); };
}
"""

# ---------------------------------------------------------------------------
# Component registration — isolate_styles=False so:
#   • our .si-root CSS is in the same document scope, no shadow DOM
#   • SVG currentColor inherits the Streamlit text color
#   • no @font-face piercing issue
# ---------------------------------------------------------------------------
_specialized_input_component = component(
    name="specialized_input",
    css=_COMPONENT_CSS,
    js=_COMPONENT_JS,
    isolate_styles=False,
)


# ---------------------------------------------------------------------------
# Internal mount helper
# ---------------------------------------------------------------------------
def _mount(
    label: str,
    value: str,
    *,
    placeholder: str,
    key: str | None,
    on_change: Callable | None,
    args: tuple | None,
    kwargs: dict | None,
    disabled: bool,
    label_visibility: Literal["visible", "hidden", "collapsed"],
    icon: str | None,  # deprecated: label-prefixed icon is intentionally not rendered
    # ruff: noqa: ARG001
    adornment_icon: str | None,  # inside-input leading icon (SVG key)
    prefix: str | None,
    suffix: str | None,
    help: str | None,
    error: str | bool | None,
    input_type: str,
    is_password: bool,
    trailing_icon: str | None,
) -> str:
    # Resolve value from session state
    current_value = value
    if key is not None:
        state = st.session_state.get(key, {})
        if isinstance(state, dict):
            current_value = state.get("value", value)

    data = {
        "label": label,
        "label_visibility": label_visibility,
        "value": current_value,
        "placeholder": placeholder,
        "disabled": disabled,
        "icon_svg": _ADORNMENT_ICONS.get(adornment_icon) if adornment_icon else None,
        "prefix": prefix,
        "suffix": suffix,
        "help": help,
        "error": error,
        "input_type": input_type,
        "is_password": is_password,
        "trailing_icon_svg": (_ADORNMENT_ICONS.get(trailing_icon) if trailing_icon else None),
        "icon_visibility": _ADORNMENT_ICONS["visibility"],
        "icon_visibility_off": _ADORNMENT_ICONS["visibility_off"],
    }

    cb: Callable | None = None
    if on_change is not None:
        _args = args or ()
        _kwargs = kwargs or {}
        cb = lambda: on_change(*_args, **_kwargs)  # noqa: E731

    result = _specialized_input_component(
        data=data,
        default={"value": current_value},
        key=key,
        on_value_change=cb if cb is not None else lambda: None,
    )

    raw = result.value if result is not None else current_value
    return raw if raw is not None else ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@extra
def specialized_text_input(
    label: str,
    value: str = "",
    *,
    placeholder: str = "",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    icon: str | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
    help: str | None = None,
    error: str | bool | None = None,
    input_type: str = "text",
) -> str:
    """
    A polished, specialized text input that matches native Streamlit styling.

    Parameters
    ----------
    label : str
        Widget label.
    icon : str | None
        Deprecated. Present for API compatibility, but label-prefixed icons are
        intentionally not rendered. Use ``adornment_icon`` (via the convenience
        wrappers) to show an icon inside the input field.
    prefix : str | None
        Text badge inside the left of the input border (e.g. ``"$"``).
    suffix : str | None
        Text badge inside the right of the input border (e.g. ``".com"``).
    help : str | None
        Tooltip text shown on hover of a right-aligned (?) icon next to the label.
    error : str | bool | None
        ``True`` → red border. ``str`` → red border + inline message.
    input_type : str
        HTML ``<input type>`` attribute.

    Returns
    -------
    str
        The current value of the input.
    """
    return _mount(
        label=label,
        value=str(value),
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=icon,
        adornment_icon=None,
        prefix=prefix,
        suffix=suffix,
        help=help,
        error=error,
        input_type=input_type,
        is_password=False,
        trailing_icon=None,
    )


def phone_input(
    label: str,
    value: str = "",
    *,
    placeholder: str = "+1 (555) 000-0000",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    help: str | None = None,
    error: str | bool | None = None,
) -> str:
    """
    Phone number input.

    The label has no prefixed icon. A small phone SVG icon appears inside the
    input field.

    Returns
    -------
    str
        The raw text value.

    Examples
    --------
    >>> phone = phone_input("Phone number", help="Include country code", key="phone")
    """
    return _mount(
        label=label,
        value=str(value),
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=None,
        adornment_icon="phone",
        prefix=None,
        suffix=None,
        help=help,
        error=error,
        input_type="tel",
        is_password=False,
        trailing_icon=None,
    )


def email_input(
    label: str,
    value: str = "",
    *,
    placeholder: str = "you@example.com",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    help: str | None = None,
    error: str | bool | None = None,
) -> str:
    """
    E-mail address input.

    Returns
    -------
    str
        The current text value.

    Examples
    --------
    >>> email = email_input("Email", key="email")
    """
    return _mount(
        label=label,
        value=str(value),
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=None,
        adornment_icon="mail",
        prefix=None,
        suffix=None,
        help=help,
        error=error,
        input_type="email",
        is_password=False,
        trailing_icon=None,
    )


def url_input(
    label: str,
    value: str = "",
    *,
    placeholder: str = "acme.com",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    help: str | None = None,
    error: str | bool | None = None,
    show_prefix: bool = True,
) -> str:
    """
    Website / URL input.

    Parameters
    ----------
    show_prefix : bool
        Show ``"https://"`` prefix badge (default ``True``).

    Returns
    -------
    str
        The current text value.

    Examples
    --------
    >>> site = url_input("Website", key="site")
    """
    return _mount(
        label=label,
        value=str(value),
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=None,
        adornment_icon=None,
        prefix="https://" if show_prefix else None,
        suffix=None,
        help=help,
        error=error,
        input_type="url",
        is_password=False,
        trailing_icon=None,
    )


def money_input(
    label: str,
    value: float | str = "",
    *,
    placeholder: str = "0.00",
    currency: str = "$",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    help: str | None = None,
    error: str | bool | None = None,
) -> float | None:
    """
    Monetary / currency input.

    Parameters
    ----------
    currency : str
        Prefix badge symbol — ``"$"``, ``"€"``, ``"£"``, ``"¥"``, ``"USD"``.

    Returns
    -------
    float | None
        Parsed numeric value, or ``None`` when empty / unparseable.

    Examples
    --------
    >>> amount = money_input("Amount", currency="€", key="amount")
    """
    str_val = "" if not value else str(value)
    raw = _mount(
        label=label,
        value=str_val,
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=None,
        adornment_icon=None,
        prefix=currency,
        suffix=None,
        help=help,
        error=error,
        input_type="number",
        is_password=False,
        trailing_icon=None,
    )
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def search_input(
    label: str,
    value: str = "",
    *,
    placeholder: str = "Search…",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    help: str | None = None,
    error: str | bool | None = None,
) -> str:
    """
    Search input.

    Returns
    -------
    str
        The current query string.

    Examples
    --------
    >>> query = search_input("Search users", label_visibility="collapsed", key="q")
    """
    return _mount(
        label=label,
        value=str(value),
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=None,
        adornment_icon="search",
        prefix=None,
        suffix=None,
        help=help,
        error=error,
        input_type="search",
        is_password=False,
        trailing_icon=None,
    )


def password_input(
    label: str,
    value: str = "",
    *,
    placeholder: str = "Enter password",
    key: str | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict[str, Any] | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    help: str | None = None,
    error: str | bool | None = None,
) -> str:
    """
    Password input with inline visibility toggle (no page rerun).

    Returns
    -------
    str
        The current password string.

    Examples
    --------
    >>> pwd = password_input("Password", help="Min. 8 characters", key="pwd")
    """
    return _mount(
        label=label,
        value=str(value),
        placeholder=placeholder,
        key=key,
        on_change=on_change,
        args=args,
        kwargs=kwargs,
        disabled=disabled,
        label_visibility=label_visibility,
        icon=None,
        adornment_icon="lock",
        prefix=None,
        suffix=None,
        help=help,
        error=error,
        input_type="password",
        is_password=True,
        trailing_icon=None,
    )


# ---------------------------------------------------------------------------
# Streamlit-extras gallery metadata
# ---------------------------------------------------------------------------


def example() -> None:
    """Gallery demo shown on the streamlit-extras website."""
    import streamlit as st

    st.text_input("Text input", placeholder="Text input", help="Help")
    st.text_input("Password input", placeholder="Password input", type="password")
    st.chat_input(placeholder="Chat input")
    pwd = password_input("Password", help="Minimum 8 characters", key="ex_pwd")
    if pwd:
        st.caption(f"Length: {len(pwd)} chars")

    email = email_input("Email address", key="ex_email", label_visibility="collapsed")
    if email:
        valid = bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))
        if not valid:
            email_input(
                "Email address (validated)",
                value=email,
                error="Please enter a valid email address.",
                key="ex_email_val",
            )

    phone_input("Phone number", help="Include your country code", key="ex_phone")
    url_input("Website", placeholder="acme.com", key="ex_url")
    amount = money_input("Amount", currency="€", help="Enter a positive value", key="ex_money")
    if amount:
        st.caption(f"Entered: {amount:.2f} €")

    q = search_input("Search", label_visibility="collapsed", key="ex_search")
    if q:
        st.caption(f"Query: {q!r}")

    specialized_text_input(
        "Bluesky handle",
        suffix=".bsky.social",
        placeholder="yourhandle",
        help="Enter your handle without the @",
        key="ex_custom",
    )


__title__ = "Specialized Inputs"
__desc__ = (
    "Polished, specialized text inputs — phone, email, URL, money, search, "
    "password — built on st.components.v2. Pixel-perfect native Streamlit styling."
)
__icon__ = "✏️"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__created_at__ = date(2026, 3, 24)
__experimental_playground__ = False
