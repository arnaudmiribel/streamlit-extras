from __future__ import annotations

import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import streamlit as st

from .. import extra

if TYPE_CHECKING:
    from collections.abc import Callable

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Comment:
    """A single comment or emoji reaction left on the app."""

    id: str
    user: str
    text: str
    selection: str  # highlighted text snippet, or "" for point comments
    page_url: str
    created_at: float = field(default_factory=time.time)
    resolved: bool = False
    reactions: dict[str, list[str]] = field(default_factory=dict)
    is_reaction: bool = False  # True when the body is an emoji reaction shortcut


# ---------------------------------------------------------------------------
# Storage protocol
# ---------------------------------------------------------------------------


class CommentStorage(ABC):
    """Abstract backend for reading and writing comments.

    Implement this to connect any persistence layer (databases, cloud stores,
    etc.).  Three batteries-included implementations ship with this extra:
    :class:`JSONFileStorage`, :class:`SessionStateStorage`, and
    :class:`LocalStorageStorage`.
    """

    @abstractmethod
    def load(self) -> list[Comment]:
        """Return all stored comments."""

    @abstractmethod
    def save(self, comments: list[Comment]) -> None:
        """Persist the full list of comments (replace-all semantics)."""

    def add(self, comment: Comment) -> None:
        """Append a comment and persist."""
        comments = self.load()
        comments.append(comment)
        self.save(comments)

    def delete(self, comment_id: str) -> None:
        """Remove a comment by id and persist."""
        self.save([c for c in self.load() if c.id != comment_id])

    def resolve(self, comment_id: str) -> None:
        """Toggle the resolved flag on a comment and persist."""
        comments = self.load()
        for c in comments:
            if c.id == comment_id:
                c.resolved = not c.resolved
        self.save(comments)

    def add_reaction(self, comment_id: str, emoji: str, user: str) -> None:
        """Toggle an emoji reaction for a user on a specific comment."""
        comments = self.load()
        for c in comments:
            if c.id == comment_id:
                users = c.reactions.setdefault(emoji, [])
                if user in users:
                    users.remove(user)
                else:
                    users.append(user)
        self.save(comments)


class JSONFileStorage(CommentStorage):
    """Persist comments as a JSON file on the local filesystem.

    Suitable for single-server deployments.  Not safe for concurrent writers.

    Args:
        path: Path to the JSON file.  Created on first write if absent.

    Example::

        storage = JSONFileStorage("comments.json")
        enable_commenting(storage=storage, user="alice")
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Comment]:
        """Return all comments from the JSON file."""
        if not self.path.exists():
            return []
        with self.path.open() as f:
            raw: list[dict[str, Any]] = json.load(f)
        return [Comment(**r) for r in raw]

    def save(self, comments: list[Comment]) -> None:
        """Write all comments back to the JSON file."""
        with self.path.open("w") as f:
            json.dump([asdict(c) for c in comments], f, indent=2)


class SessionStateStorage(CommentStorage):
    """Ephemeral in-process storage kept in ``st.session_state``.

    Comments survive reruns but are lost when the server restarts.
    Useful for demos, tests, and single-user local apps.

    Example::

        storage = SessionStateStorage()
        enable_commenting(storage=storage, user="alice")
    """

    _KEY = "_st_commenting_session"

    def load(self) -> list[Comment]:
        """Return comments from session state."""
        return [Comment(**r) for r in st.session_state.get(self._KEY, [])]

    def save(self, comments: list[Comment]) -> None:
        """Persist comments to session state."""
        st.session_state[self._KEY] = [asdict(c) for c in comments]


class LocalStorageStorage(CommentStorage):
    """Persist comments in the browser's ``localStorage``.

    Comments survive server restarts and are scoped to the browser that created
    them — making this ideal for single-user apps deployed on Streamlit Cloud
    where you don't want to maintain a server-side database.

    Because ``localStorage`` is only readable asynchronously (the JS value must
    round-trip to Python via a CCv2 trigger), this backend pre-loads comments
    from the browser into ``st.session_state`` on the first rerun of each
    session, then operates synchronously from there and flushes back to
    ``localStorage`` on every write.

    Args:
        storage_key: The ``localStorage`` key used to store the JSON blob.
            Override if you run multiple apps on the same domain.

    Example::

        storage = LocalStorageStorage()
        enable_commenting(storage=storage, user="alice")
    """

    _LS_READY_KEY = "_st_commenting_ls_ready"
    _LS_CACHE_KEY = "_st_commenting_ls_cache"
    _LS_COMPONENT_KEY = "_st_commenting_ls_component"

    # CCv2 component registered once at class level — handles localStorage I/O.
    # On every mount it pushes the current localStorage value back as state,
    # and if `write_json` is present in data it persists it immediately.
    _LS_COMPONENT = st.components.v2.component(
        "st_commenting_localstorage",
        html="<div></div>",
        js="""
export default function (component) {
  const { data, setStateValue } = component;
  const storageKey = (data && data.storage_key) || "st_commenting_data";

  // Always push current value to Python so load() can read it.
  const raw = localStorage.getItem(storageKey);
  setStateValue("stored_json", raw || "[]");

  // If Python sent new data, persist it.
  if (data && data.write_json != null) {
    localStorage.setItem(storageKey, data.write_json);
  }
}
""",
    )

    def __init__(self, storage_key: str = "st_commenting_data") -> None:
        self.storage_key = storage_key

    def _mount(self, write_json: str | None = None) -> None:
        """Mount the localStorage helper component (zero-height via st._event)."""
        with st._event:  # type: ignore[attr-defined]
            result = self._LS_COMPONENT(
                key=self._LS_COMPONENT_KEY,
                data={"storage_key": self.storage_key, "write_json": write_json},
                on_stored_json_change=lambda: None,
            )
        if not st.session_state.get(self._LS_READY_KEY) and result.stored_json:
            try:
                raw = json.loads(result.stored_json)
                st.session_state[self._LS_CACHE_KEY] = [Comment(**r) for r in raw]
            except (json.JSONDecodeError, TypeError):
                st.session_state[self._LS_CACHE_KEY] = []
            st.session_state[self._LS_READY_KEY] = True

    def load(self) -> list[Comment]:
        """Return comments bootstrapped from localStorage into session cache."""
        self._mount()
        return list(st.session_state.get(self._LS_CACHE_KEY, []))

    def save(self, comments: list[Comment]) -> None:
        """Write to session cache and flush to localStorage immediately."""
        st.session_state[self._LS_CACHE_KEY] = comments
        write_json = json.dumps([asdict(c) for c in comments], indent=2)
        self._mount(write_json=write_json)


# ---------------------------------------------------------------------------
# CCv2 main component — registered once at module level
# ---------------------------------------------------------------------------

_HTML = "<div id='st-commenting-root'></div>"

_JS = """
export default function (component) {
  const { data, parentElement, setTriggerValue } = component;

  const reactions = (data && data.reactions)   || ["👍", "❤️", "💡", "🔥"];
  const position  = (data && data.position)    || "bottom-right";
  const comments  = (data && data.comments)    || [];
  const panelOpen = (data && data.panel_open)  || false;
  const panelMin  = (data && data.panel_min)   || false;

  // ── Material Symbols font (injected once per document) ───────────────────

  if (!document.getElementById("st-commenting-font")) {
    const link = document.createElement("link");
    link.id   = "st-commenting-font";
    link.rel  = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200";
    document.head.appendChild(link);
  }

  // ── Shared helpers ───────────────────────────────────────────────────────

  const mdIcon = (name, size) => {
    const el = document.createElement("span");
    el.className = "material-symbols-outlined";
    el.textContent = name;
    el.style.cssText = `font-size:${size || "18px"};line-height:1;vertical-align:middle;user-select:none;`;
    return el;
  };

  const iconBtn = (iconName, title, extraStyles) => {
    const b = document.createElement("button");
    b.appendChild(mdIcon(iconName));
    b.title = title;
    Object.assign(b.style, {
      background: "none", border: "none", cursor: "pointer",
      padding: "4px", borderRadius: "4px", color: "inherit",
      display: "flex", alignItems: "center", justifyContent: "center",
      opacity: "0.65", transition: "opacity 0.15s",
      ...(extraStyles || {}),
    });
    b.onmouseenter = () => { b.style.opacity = "1"; b.style.background = "var(--secondary-background-color, #f0f2f6)"; };
    b.onmouseleave = () => { b.style.opacity = "0.65"; b.style.background = "none"; };
    return b;
  };

  // ── Floating panel ───────────────────────────────────────────────────────

  const panelId = "st-commenting-panel";
  let panel = document.getElementById(panelId);
  if (!panel) {
    panel = document.createElement("div");
    panel.id = panelId;
    const [vert, horiz] = position.split("-");
    Object.assign(panel.style, {
      position: "fixed", [vert]: "20px", [horiz]: "20px",
      zIndex: "99999", fontFamily: "var(--font, sans-serif)", fontSize: "14px",
      color: "var(--text-color, #31333f)",
      display: "flex", flexDirection: "column",
      alignItems: horiz === "right" ? "flex-end" : "flex-start",
      gap: "8px", pointerEvents: "none",
    });
    document.body.appendChild(panel);
  }

  // ── Inline popover ───────────────────────────────────────────────────────

  const popoverId = "st-commenting-popover";
  let popover = document.getElementById(popoverId);
  if (!popover) {
    popover = document.createElement("div");
    popover.id = popoverId;
    Object.assign(popover.style, {
      position: "fixed", zIndex: "100000",
      background: "var(--background-color, #ffffff)",
      border: "1px solid var(--secondary-background-color, #e0e0e0)",
      borderRadius: "10px", boxShadow: "0 4px 24px rgba(0,0,0,0.13)",
      padding: "12px 14px", display: "none",
      flexDirection: "column", gap: "8px",
      minWidth: "240px", maxWidth: "320px", pointerEvents: "all",
    });
    document.body.appendChild(popover);
  }

  function hidePopover() {
    popover.style.display = "none";
    popover.innerHTML = "";
  }

  function showPopover(x, y, selectedText) {
    popover.innerHTML = "";
    popover.style.display = "flex";

    // Header row: label + close button
    const header = document.createElement("div");
    Object.assign(header.style, {
      display: "flex", justifyContent: "space-between", alignItems: "center",
    });
    const headerLabel = document.createElement("span");
    Object.assign(headerLabel.style, { fontWeight: "600", fontSize: "13px" });
    headerLabel.textContent = "Add comment";
    const headerClose = iconBtn("close", "Dismiss", hidePopover);
    headerClose.style.marginRight = "-2px";
    header.appendChild(headerLabel);
    header.appendChild(headerClose);
    popover.appendChild(header);

    // Selection preview
    if (selectedText) {
      const preview = document.createElement("div");
      Object.assign(preview.style, {
        fontSize: "12px",
        borderLeft: "3px solid var(--primary-color, #ff4b4b)",
        paddingLeft: "8px", fontStyle: "italic",
        maxHeight: "40px", overflow: "hidden", wordBreak: "break-word",
        opacity: "0.65",
      });
      preview.textContent = selectedText.length > 120
        ? selectedText.slice(0, 117) + "\u2026" : selectedText;
      popover.appendChild(preview);
    }

    // Emoji reactions - small circles, no divider
    const emojiRow = document.createElement("div");
    Object.assign(emojiRow.style, { display: "flex", gap: "5px", flexWrap: "wrap" });
    reactions.forEach(emoji => {
      const eb = document.createElement("button");
      eb.textContent = emoji;
      Object.assign(eb.style, {
        fontSize: "15px",
        background: "rgba(128,128,128,0.07)",
        border: "1px solid rgba(128,128,128,0.18)",
        borderRadius: "50%",
        cursor: "pointer",
        width: "34px", height: "34px",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: "0",
        transition: "background 0.12s, transform 0.1s",
        flexShrink: "0",
      });
      eb.onmouseenter = () => { eb.style.background = "rgba(128,128,128,0.15)"; eb.style.transform = "scale(1.15)"; };
      eb.onmouseleave = () => { eb.style.background = "rgba(128,128,128,0.07)"; eb.style.transform = "scale(1)"; };
      eb.onclick = () => {
        setTriggerValue("new_comment", { text: emoji, selection: selectedText || "", is_reaction: true });
        hidePopover();
      };
      emojiRow.appendChild(eb);
    });
    popover.appendChild(emojiRow);

    // Textarea
    const textarea = document.createElement("textarea");
    Object.assign(textarea.style, {
      resize: "none", width: "100%", minHeight: "64px",
      border: "1px solid var(--secondary-background-color, #e0e0e0)",
      borderRadius: "6px", padding: "6px 8px", fontSize: "13px",
      fontFamily: "inherit", color: "inherit",
      background: "var(--secondary-background-color, #f0f2f6)",
      boxSizing: "border-box", outline: "none",
    });
    textarea.placeholder = "Add a comment…";
    popover.appendChild(textarea);

    // Submit
    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Comment";
    Object.assign(submitBtn.style, {
      alignSelf: "flex-end",
      background: "var(--primary-color, #ff4b4b)", color: "#fff",
      border: "none", borderRadius: "6px", padding: "5px 14px",
      cursor: "pointer", fontSize: "13px", fontWeight: "600",
    });
    submitBtn.onclick = () => {
      const text = textarea.value.trim();
      if (!text) return;
      setTriggerValue("new_comment", { text, selection: selectedText || "", is_reaction: false });
      hidePopover();
    };
    popover.appendChild(submitBtn);

    // Position
    const ph = popover.offsetHeight || 200, pw = popover.offsetWidth || 260;
    let left = x + 8, top = y + 8;
    if (left + pw > window.innerWidth  - 16) left = x - pw - 8;
    if (top  + ph > window.innerHeight - 16) top  = y - ph - 8;
    popover.style.left = left + "px";
    popover.style.top  = top  + "px";
    setTimeout(() => textarea.focus(), 50);
  }

  // ── Panel rendering ──────────────────────────────────────────────────────

  function renderPanel() {
    panel.innerHTML = "";
    panel.style.pointerEvents = "all";

    const activeCount = comments.filter(c => !c.resolved).length;

    // Badge / header bar
    const bar = document.createElement("div");
    Object.assign(bar.style, {
      display: "flex", alignItems: "center", gap: "2px",
      background: "var(--background-color, #fff)",
      border: "1px solid var(--secondary-background-color, #e0e0e0)",
      borderRadius: "20px", padding: "5px 8px 5px 14px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.10)",
    });

    const label = document.createElement("span");
    label.style.cssText = "font-size:13px;font-weight:600;flex:1;white-space:nowrap;margin-right:4px;";
    label.textContent = activeCount === 0
      ? "No comment yet."
      : `${activeCount} comment${activeCount !== 1 ? "s" : ""}`;
    bar.appendChild(label);

    if (!panelOpen) {
      const openBtn = iconBtn("chat_bubble", "Show comments");
      openBtn.onclick = () => setTriggerValue("panel_toggled", { open: true, minimized: false });
      bar.appendChild(openBtn);
    } else {
      const minBtn = iconBtn(panelMin ? "expand_less" : "expand_more", panelMin ? "Expand" : "Minimize");
      minBtn.onclick = () => setTriggerValue("panel_toggled", { open: true, minimized: !panelMin });
      bar.appendChild(minBtn);

      const closeBtn = iconBtn("close", "Close");
      closeBtn.onclick = () => setTriggerValue("panel_toggled", { open: false, minimized: false });
      bar.appendChild(closeBtn);
    }

    panel.appendChild(bar);

    // Comment list
    if (!panelOpen || panelMin || !comments.length) return;

    const list = document.createElement("div");
    Object.assign(list.style, {
      background: "var(--background-color, #fff)",
      border: "1px solid var(--secondary-background-color, #e0e0e0)",
      borderRadius: "12px", boxShadow: "0 4px 24px rgba(0,0,0,0.12)",
      padding: "8px 0", maxHeight: "420px", overflowY: "auto",
      width: "300px",
    });

    comments.forEach(c => {
      const item = document.createElement("div");
      Object.assign(item.style, {
        padding: "10px 14px",
        borderBottom: "1px solid var(--secondary-background-color, #f0f2f6)",
        opacity: c.resolved ? "0.45" : "1",
      });

      // Meta row
      const meta = document.createElement("div");
      Object.assign(meta.style, { display: "flex", justifyContent: "space-between", marginBottom: "4px", gap: "8px" });
      const author = document.createElement("span");
      author.textContent = c.user;
      author.style.cssText = "font-weight:600;font-size:12px;";
      const ts = document.createElement("span");
      ts.textContent = new Date(c.created_at * 1000).toLocaleDateString();
      ts.style.cssText = "font-size:11px;opacity:0.55;white-space:nowrap;";
      meta.appendChild(author);
      meta.appendChild(ts);
      item.appendChild(meta);

      // Selection quote
      if (c.selection) {
        const quote = document.createElement("div");
        Object.assign(quote.style, {
          fontSize: "11px",
          borderLeft: "3px solid var(--primary-color, #ff4b4b)",
          paddingLeft: "6px", marginBottom: "4px",
          fontStyle: "italic", opacity: "0.7", wordBreak: "break-word",
        });
        quote.textContent = c.selection.length > 80
          ? c.selection.slice(0, 77) + "…" : c.selection;
        item.appendChild(quote);
      }

      // Body
      const body = document.createElement("div");
      body.textContent = c.text;
      body.style.cssText = "font-size:13px;word-break:break-word;margin-bottom:6px;";
      item.appendChild(body);

      // Action row
      const actions = document.createElement("div");
      actions.style.cssText = "display:flex;gap:2px;";

      const resolveBtn = iconBtn(c.resolved ? "undo" : "check_circle", c.resolved ? "Reopen" : "Resolve");
      resolveBtn.onclick = () => setTriggerValue("resolve_comment", { id: c.id });

      const deleteBtn = iconBtn("delete", "Delete");
      deleteBtn.onclick = () => setTriggerValue("delete_comment", { id: c.id });

      actions.appendChild(resolveBtn);
      actions.appendChild(deleteBtn);
      item.appendChild(actions);
      list.appendChild(item);
    });

    panel.appendChild(list);
  }

  renderPanel();

  // ── Global event listeners ───────────────────────────────────────────────

  function onMouseUp(e) {
    if (popover.contains(e.target) || panel.contains(e.target)) return;
    const sel = window.getSelection();
    const selectedText = sel ? sel.toString().trim() : "";
    if (selectedText.length > 0) showPopover(e.clientX, e.clientY, selectedText);
  }

  function onContextMenu(e) {
    if (popover.contains(e.target) || panel.contains(e.target)) return;
    e.preventDefault();
    const sel = window.getSelection();
    showPopover(e.clientX, e.clientY, sel ? sel.toString().trim() : "");
  }

  function onKeyDown(e) {
    if (e.key === "Escape") hidePopover();
  }

  function onDocClick(e) {
    if (!popover.contains(e.target) && !panel.contains(e.target)) hidePopover();
  }

  // Use window + capture:true so events aren't swallowed by shadow DOM
  // or iframes that Streamlit uses for some internal elements.
  window.addEventListener("mouseup",     onMouseUp,     true);
  window.addEventListener("contextmenu", onContextMenu, true);
  window.addEventListener("keydown",     onKeyDown,     true);
  window.addEventListener("click",       onDocClick,    true);

  return () => {
    window.removeEventListener("mouseup",     onMouseUp,     true);
    window.removeEventListener("contextmenu", onContextMenu, true);
    window.removeEventListener("keydown",     onKeyDown,     true);
    window.removeEventListener("click",       onDocClick,    true);
    panel.remove();
    popover.remove();
  };
}
"""

_COMMENTING_COMPONENT = st.components.v2.component(
    "st_commenting",
    html=_HTML,
    js=_JS,
)

# ---------------------------------------------------------------------------
# Python API
# ---------------------------------------------------------------------------

_DEFAULT_REACTIONS = ["👍", "❤️", "💡", "🔥"]
_COMPONENT_KEY = "_st_commenting_component"


@extra
def enable_commenting(
    storage: CommentStorage,
    user: str = "anonymous",
    *,
    reactions: list[str] | None = None,
    position: str = "bottom-right",
    form_builder: Callable[[], dict[str, Any] | None] | None = None,
    key: str = _COMPONENT_KEY,
) -> None:
    """Enable collaborative commenting anywhere in a Streamlit app.

    Call once at the top of your script (or in a shared ``utils.py``).
    A floating panel shows all comments; selecting text or right-clicking
    anywhere opens an inline popover for adding comments or emoji reactions.

    When ``form_builder`` is provided it is called inside a ``st.dialog``
    whenever the user submits a text comment (not an emoji reaction).  Use
    ``st.form`` inside the callable for multi-field layouts with a single
    submit button.  Return a dict with at least a ``"text"`` key, or
    ``None`` to cancel.

    Args:
        storage: Backend that loads and saves :class:`Comment` objects.
            Use :class:`JSONFileStorage`, :class:`SessionStateStorage`,
            :class:`LocalStorageStorage`, or your own subclass.
        user: Display name for the current user.
        reactions: Emoji strings shown in the inline popover.
            Defaults to ``["👍", "❤️", "💡", "🔥"]``.
        position: Where the floating panel is anchored.  One of
            ``"bottom-right"`` (default), ``"bottom-left"``,
            ``"top-right"``, ``"top-left"``.
        form_builder: Optional callable rendered inside a ``st.dialog``.
            Must return ``{"text": ...}`` on submit or ``None`` to cancel.
        key: Component key.  Override only for multiple independent
            instances in the same app.

    Example::

        from streamlit_extras.commenting import enable_commenting, JSONFileStorage

        enable_commenting(
            storage=JSONFileStorage("comments.json"),
            user=st.session_state.get("username", "anonymous"),
        )
    """
    if reactions is None:
        reactions = _DEFAULT_REACTIONS

    _panel_open_key = f"{key}_panel_open"
    _panel_min_key = f"{key}_panel_min"
    _pending_key = f"{key}_pending_comment"

    panel_open: bool = st.session_state.get(_panel_open_key, False)
    panel_min: bool = st.session_state.get(_panel_min_key, False)

    comments = storage.load()

    # Mount invisibly — st._event gives zero layout height (private API,
    # same pattern used by local_storage_manager, redirect, scroll_to_element).
    with st._event:  # type: ignore[attr-defined]
        result = _COMMENTING_COMPONENT(
            key=key,
            data={
                "comments": [asdict(c) for c in comments],
                "reactions": reactions,
                "position": position,
                "panel_open": panel_open,
                "panel_min": panel_min,
            },
            on_new_comment_change=lambda: None,
            on_panel_toggled_change=lambda: None,
            on_resolve_comment_change=lambda: None,
            on_delete_comment_change=lambda: None,
        )

    # ── Handle triggers ──────────────────────────────────────────────────────

    if result.new_comment:
        payload = result.new_comment
        if form_builder and not payload.get("is_reaction"):
            st.session_state[_pending_key] = payload
            st.rerun()
        else:
            _persist_comment(storage, user, payload)
            st.rerun()

    if result.panel_toggled:
        st.session_state[_panel_open_key] = result.panel_toggled.get("open", False)
        st.session_state[_panel_min_key] = result.panel_toggled.get("minimized", False)
        st.rerun()

    if result.resolve_comment:
        storage.resolve(result.resolve_comment["id"])
        st.rerun()

    if result.delete_comment:
        storage.delete(result.delete_comment["id"])
        st.rerun()

    # ── Optional native-Streamlit comment dialog ─────────────────────────────
    if form_builder and _pending_key in st.session_state:
        pending = st.session_state[_pending_key]

        @st.dialog("Add comment")
        def _comment_dialog() -> None:
            if pending.get("selection"):
                st.markdown(f"> *{pending['selection'][:120]}{'…' if len(pending['selection']) > 120 else ''}*")
            result_fields = form_builder()
            if result_fields is not None:
                del st.session_state[_pending_key]
                _persist_comment(
                    storage,
                    user,
                    {
                        "text": str(result_fields.get("text", "")),
                        "selection": pending.get("selection", ""),
                        "is_reaction": False,
                    },
                )
                st.rerun()

        _comment_dialog()


def _persist_comment(
    storage: CommentStorage,
    user: str,
    payload: dict[str, Any],
) -> None:
    page_url = ""
    if hasattr(st, "context") and hasattr(st.context, "url"):
        page_url = st.context.url
    storage.add(
        Comment(
            id=str(uuid.uuid4()),
            user=user,
            text=payload.get("text", ""),
            selection=payload.get("selection", ""),
            page_url=page_url,
            is_reaction=payload.get("is_reaction", False),
        )
    )


# ---------------------------------------------------------------------------
# Gallery examples
# ---------------------------------------------------------------------------


def example_simple() -> None:
    """Basic demo with session-state storage and default settings."""
    st.markdown(
        "### Commenting demo\n\n"
        "Select any text or **right-click** anywhere to leave a comment or "
        "emoji reaction.  Use the floating panel (bottom-right) to browse, "
        "resolve, or delete comments."
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lorem ipsum")
        st.write(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        )
    with col2:
        st.subheader("Some numbers")
        st.metric("Revenue", "$42,000", "+12%")
        st.metric("Users", "1,234", "+5%")

    enable_commenting(
        storage=SessionStateStorage(),
        user="demo-user",
        reactions=["👍", "❤️", "💡", "🔥", "🤔"],
    )


def example_custom_form() -> None:
    """Demo with a custom multi-field Streamlit form inside a dialog.

    The ``form_builder`` callable is wrapped in ``st.form`` so all fields
    submit together with a single button.
    """
    st.markdown(
        "### Custom form demo\n\n"
        "Select text or right-click to comment.  The comment form is a "
        "native Streamlit ``st.form`` with extra fields rendered inside "
        "a ``st.dialog``."
    )
    st.write(
        "Streamlit makes it easy to annotate content collaboratively. "
        "Select this sentence and add a tagged comment to try it out!"
    )

    def build_form() -> dict[str, Any] | None:
        with st.form("comment_form"):
            text = st.text_area("Comment", placeholder="Your thoughts…")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            category = st.selectbox("Category", ["Bug", "Suggestion", "Question", "Praise"])
            submitted = st.form_submit_button("Submit")
        if submitted and text.strip():
            return {"text": f"[{priority} / {category}] {text.strip()}"}
        return None

    enable_commenting(
        storage=SessionStateStorage(),
        user="demo-user",
        form_builder=build_form,
        key="_st_commenting_custom",
    )


def example() -> None:
    """Default gallery example — runs the simple demo."""
    example_simple()


__title__ = "Commenting"
__desc__ = (
    "Enable collaborative comments and emoji reactions anywhere in a Streamlit "
    "app — inline popovers on text selection or right-click, a floating panel "
    "to browse, resolve, and delete comments, and pluggable storage backends "
    "including browser localStorage."
)
__icon__ = "💬"
__examples__ = [example_simple, example_custom_form]
__author__ = "Arnaud Miribel"
__experimental_playground__ = False
