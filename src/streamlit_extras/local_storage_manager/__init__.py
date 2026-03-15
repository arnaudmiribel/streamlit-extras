"""Read and write browser localStorage from Python.

A Streamlit Custom Component v2 (CCv2) that manages browser localStorage,
providing a dict-like interface to read, set, and delete data with automatic
JSON serialization.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, MutableMapping
from typing import Any

import streamlit as st
from streamlit.errors import StreamlitAPIException

from streamlit_extras import extra

_MAX_VALUE_SIZE_BYTES = 1_000_000  # 1MB soft limit per value
_STORAGE_PREFIX = "st_extras_"


_LOCAL_STORAGE_COMPONENT = st.components.v2.component(
    name="streamlit_extras.local_storage_manager",
    html="<div aria-hidden='true'></div>",
    js="""
    const STORAGE_PREFIX = "st_extras_";

    function getAppPrefix() {
        // Use pathname as app identifier to namespace storage
        const path = window.location.pathname || "/";
        // Sanitize path for use as prefix
        const sanitized = path.replace(/[^a-zA-Z0-9]/g, "_");
        return STORAGE_PREFIX + sanitized + "_";
    }

    function parseStoredValue(value) {
        if (value === null || value === undefined) {
            return null;
        }
        try {
            return JSON.parse(value);
        } catch (_error) {
            // Return as string if not valid JSON
            return value;
        }
    }

    function getSnapshot(prefix) {
        const snapshot = {};
        for (let i = 0; i < localStorage.length; i++) {
            const fullKey = localStorage.key(i);
            if (fullKey && fullKey.startsWith(prefix)) {
                const key = fullKey.slice(prefix.length);
                const rawValue = localStorage.getItem(fullKey);
                snapshot[key] = parseStoredValue(rawValue);
            }
        }
        return snapshot;
    }

    function serializeSnapshot(snapshot) {
        const sortedEntries = Object.entries(snapshot).sort(([left], [right]) =>
            left.localeCompare(right)
        );
        return JSON.stringify(Object.fromEntries(sortedEntries));
    }

    function setItem(prefix, name, value) {
        const fullKey = prefix + name;
        const serialized = JSON.stringify(value);
        try {
            localStorage.setItem(fullKey, serialized);
            return true;
        } catch (error) {
            // QuotaExceededError
            console.error("localStorage quota exceeded:", error);
            return false;
        }
    }

    function deleteItem(prefix, name) {
        const fullKey = prefix + name;
        localStorage.removeItem(fullKey);
    }

    function clearAll(prefix) {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const fullKey = localStorage.key(i);
            if (fullKey && fullKey.startsWith(prefix)) {
                keysToRemove.push(fullKey);
            }
        }
        keysToRemove.forEach(key => localStorage.removeItem(key));
    }

    export default function (component) {
        const { data, setStateValue } = component;

        const prefix = getAppPrefix();
        const operations = data?.operations ?? [];
        let lastProcessedOperationId = data?.last_processed_operation_id ?? 0;

        operations.forEach((operation) => {
            if (operation.type === "set") {
                setItem(prefix, operation.name, operation.value);
            } else if (operation.type === "delete") {
                deleteItem(prefix, operation.name);
            } else if (operation.type === "clear") {
                clearAll(prefix);
            }

            lastProcessedOperationId = Math.max(
                lastProcessedOperationId,
                operation.id ?? lastProcessedOperationId
            );
        });

        const snapshot = getSnapshot(prefix);

        setStateValue("ready", true);
        setStateValue("snapshot_json", serializeSnapshot(snapshot));
        setStateValue("last_processed_operation_id", lastProcessedOperationId);

        return () => {};
    }
    """,
)


def _state_key(component_key: str) -> str:
    return f"{component_key}__local_storage_state"


def _validate_key(name: str) -> None:
    if not name:
        raise StreamlitAPIException("Storage keys must not be empty.")

    if not isinstance(name, str):
        raise StreamlitAPIException("Storage keys must be strings.")


def _validate_value(value: Any) -> None:
    try:
        serialized = json.dumps(value)
    except (TypeError, ValueError) as e:
        raise StreamlitAPIException(f"Value must be JSON-serializable: {e}") from e

    if len(serialized.encode("utf-8")) > _MAX_VALUE_SIZE_BYTES:
        raise StreamlitAPIException(
            f"Value exceeds the recommended size limit of {_MAX_VALUE_SIZE_BYTES // 1_000_000}MB. "
            "Large values may cause performance issues or exceed browser storage limits."
        )


class LocalStorageManager(MutableMapping[str, Any]):
    """A dict-like interface for managing browser localStorage.

    The LocalStorageManager provides read/write access to browser localStorage through
    a MutableMapping interface. Values are automatically serialized to/from JSON,
    so you can store dicts, lists, strings, numbers, and booleans directly.

    Note:
        - Data is namespaced per-app (based on URL path) to prevent collisions
        - Total storage limit is ~5-10MB depending on browser
        - Data persists until explicitly cleared (survives page refresh/browser restart)
    """

    def __init__(self, key: str) -> None:
        self._key = key
        self._store_key = _state_key(key)
        self._store = st.session_state.setdefault(
            self._store_key,
            {"next_operation_id": 1, "pending_operations": []},
        )

        component_state = st.session_state.get(key, {})
        last_processed_operation_id = component_state.get("last_processed_operation_id", 0)
        if last_processed_operation_id:
            self._store["pending_operations"] = [
                operation
                for operation in self._store["pending_operations"]
                if operation["id"] > last_processed_operation_id
            ]

        default_snapshot_json = component_state.get("snapshot_json", "{}")
        default_ready = component_state.get("ready", False)

        self._result = _LOCAL_STORAGE_COMPONENT(
            key=key,
            data={
                "operations": self._store["pending_operations"],
                "last_processed_operation_id": last_processed_operation_id,
            },
            default={
                "ready": default_ready,
                "snapshot_json": default_snapshot_json,
                "last_processed_operation_id": last_processed_operation_id,
            },
            on_ready_change=lambda: None,
            on_snapshot_json_change=lambda: None,
            on_last_processed_operation_id_change=lambda: None,
            height=0,
        )

        self._ready = bool(self._result.ready)
        self._snapshot = json.loads(self._result.snapshot_json or "{}")

    def ready(self) -> bool:
        """Check if the storage manager has synced with the browser.

        Returns:
            True if localStorage has been loaded from the browser, False otherwise.
        """
        return self._ready

    def set(self, name: str, value: Any) -> None:
        """Set a value in localStorage.

        Args:
            name: The storage key.
            value: Any JSON-serializable value (dict, list, str, int, float, bool, None).
        """
        _validate_key(name)
        _validate_value(value)

        self._queue_operation(
            operation_type="set",
            name=name,
            value=value,
        )

    def delete(self, name: str) -> None:
        """Delete an item from localStorage.

        Args:
            name: The storage key to delete.
        """
        _validate_key(name)

        self._queue_operation(
            operation_type="delete",
            name=name,
            value=None,
        )

    def clear(self) -> None:
        """Clear all items from this app's localStorage namespace.

        This only clears items belonging to this app, not all localStorage data.
        """
        self._queue_operation(
            operation_type="clear",
            name="",
            value=None,
        )

    def _queue_operation(
        self,
        *,
        operation_type: str,
        name: str,
        value: Any,
    ) -> None:
        operation_id = self._store["next_operation_id"]
        self._store["next_operation_id"] += 1
        self._store["pending_operations"].append(
            {
                "id": operation_id,
                "type": operation_type,
                "name": name,
                "value": value,
            }
        )

    def __getitem__(self, key: str) -> Any:
        return self._snapshot[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        if key not in self._snapshot:
            raise KeyError(key)
        self.delete(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._snapshot)

    def __len__(self) -> int:
        return len(self._snapshot)

    def __repr__(self) -> str:
        return repr(self._snapshot)


@extra
def local_storage_manager(*, key: str = "local_storage_manager") -> LocalStorageManager:
    """Create a localStorage manager to read and write browser localStorage from Python.

    This component provides a dict-like interface for managing browser localStorage.
    Unlike cookies (~4KB limit), localStorage can store ~5-10MB of data. Values are
    automatically serialized to/from JSON, so you can store dicts, lists, and primitives.

    The returned ``LocalStorageManager`` implements Python's ``MutableMapping`` protocol,
    so you can use it like a dictionary:

    - ``manager["key"]`` - get a value (raises ``KeyError`` if not found)
    - ``manager.get("key", default)`` - get with a default value
    - ``manager["key"] = value`` - set a value (auto-serialized to JSON)
    - ``del manager["key"]`` - delete a key
    - ``"key" in manager`` - check if a key exists
    - ``len(manager)`` - count of stored items
    - ``dict(manager)`` - convert to a regular dict
    - ``manager.keys()``, ``manager.values()``, ``manager.items()`` - iterate
    - ``manager.clear()`` - remove all items for this app

    Data is automatically namespaced per-app (based on URL path) to prevent
    collisions between different Streamlit apps on the same domain.

    Args:
        key: A unique key for this component instance. Defaults to "local_storage_manager".
            Use different keys if you need multiple independent storage managers.

    Returns:
        A LocalStorageManager instance that provides dict-like access to localStorage.

    Note:
        - Call ``manager.ready()`` to check if data has synced from the browser
        - Use ``st.stop()`` on first load while waiting for sync
        - After setting/deleting values, call ``st.rerun()`` to see changes
        - Data persists across page refreshes and browser sessions

    Example:
        >>> manager = local_storage_manager()
        >>> if not manager.ready():
        ...     st.stop()  # Wait for browser sync
        >>> settings = manager.get("settings", {"theme": "light"})
        >>> if st.button("Use dark theme"):
        ...     settings["theme"] = "dark"
        ...     manager["settings"] = settings
        ...     st.rerun()

    Example with progress tracking:
        >>> manager = local_storage_manager()
        >>> if manager.ready():
        ...     progress = manager.get("game_progress", {"level": 1, "score": 0})
        ...     st.write(f"Level {progress['level']}, Score: {progress['score']}")
    """
    return LocalStorageManager(key=key)


def example() -> None:
    """Example usage of the local_storage_manager component."""
    st.info(
        "localStorage can store ~5-10MB of data (vs ~4KB for cookies). "
        "Data persists across page refreshes and browser sessions."
    )

    manager = local_storage_manager(key="demo_local_storage")

    if not manager.ready():
        st.info("Syncing localStorage from browser. The app will be ready on the next rerun.")
        st.stop()

    st.subheader("Current localStorage")
    st.json(dict(manager))

    get_col, set_col, delete_col = st.columns(3)

    with get_col:
        st.markdown("**Get value**")
        get_key = st.text_input("Key", key="storage_get_key")
        if st.button("Read value", key="storage_get_button"):
            value = manager.get(get_key)
            if value is not None:
                st.write(value)
            else:
                st.write("*Not found*")

    with set_col:
        st.markdown("**Set value**")
        set_key = st.text_input("Key", key="storage_set_key")
        set_value = st.text_area("Value (JSON)", key="storage_set_value", height=100)
        if st.button("Write value", key="storage_set_button"):
            try:
                # Try to parse as JSON, otherwise store as string
                try:
                    parsed_value = json.loads(set_value)
                except json.JSONDecodeError:
                    parsed_value = set_value
                manager[set_key] = parsed_value
                st.rerun()
            except StreamlitAPIException as e:
                st.error(str(e))

    with delete_col:
        st.markdown("**Delete value**")
        delete_key = st.text_input("Key to delete", key="storage_delete_key")
        if st.button("Delete", key="storage_delete_button"):
            manager.delete(delete_key)
            st.rerun()
        if st.button("Clear all", key="storage_clear_button"):
            manager.clear()
            st.rerun()

    st.subheader("Basic usage")
    st.code(
        """
manager = local_storage_manager()

if not manager.ready():
    st.stop()  # Wait for browser sync

# Store any JSON-serializable data
settings = manager.get("settings", {"theme": "light", "lang": "en"})
st.write(f"Current theme: {settings['theme']}")

if st.button("Use dark theme"):
    settings["theme"] = "dark"
    manager["settings"] = settings
    st.rerun()

# Track user progress
progress = manager.get("progress", {"level": 1, "score": 0})
if st.button("Complete level"):
    progress["level"] += 1
    progress["score"] += 100
    manager["progress"] = progress
    st.rerun()
""".strip(),
        language="python",
    )


__title__ = "Local Storage Manager"
__desc__ = "Read and write browser localStorage from Python with automatic JSON serialization."
__icon__ = "💾"
__examples__ = [example]
__author__ = "Lukas Masuch"
__streamlit_min_version__ = "1.46.0"
