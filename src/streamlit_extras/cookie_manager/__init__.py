"""Read and write browser cookies from Python.

A Streamlit Custom Component v2 (CCv2) that manages browser cookies,
providing a dict-like interface to read, set, and delete cookies from Python.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, MutableMapping
from datetime import date, datetime, timedelta
from typing import Literal, cast
from urllib.parse import quote

import streamlit as st
import streamlit.components.v2
from streamlit.errors import StreamlitAPIException

from streamlit_extras import extra

_MAX_COOKIE_SIZE_BYTES = 4096
_VALID_SAMESITE_VALUES = {"strict", "lax", "none"}


_COOKIE_MANAGER_COMPONENT = st.components.v2.component(
    name="streamlit_extras.cookie_manager",
    html="<div aria-hidden='true'></div>",
    js="""
    function decodeCookiePart(value) {
        try {
            return decodeURIComponent(value);
        } catch (_error) {
            return value;
        }
    }

    function parseCookies() {
        const snapshot = {};
        const rawCookie = document.cookie || "";
        if (!rawCookie.trim()) {
            return snapshot;
        }

        rawCookie.split(";").forEach((part) => {
            const trimmed = part.trim();
            if (!trimmed) {
                return;
            }

            const separatorIndex = trimmed.indexOf("=");
            const rawName =
                separatorIndex >= 0 ? trimmed.slice(0, separatorIndex) : trimmed;
            const rawValue =
                separatorIndex >= 0 ? trimmed.slice(separatorIndex + 1) : "";

            snapshot[decodeCookiePart(rawName)] = decodeCookiePart(rawValue);
        });

        return snapshot;
    }

    function serializeSnapshot(snapshot) {
        const sortedEntries = Object.entries(snapshot).sort(([left], [right]) =>
            left.localeCompare(right)
        );
        return JSON.stringify(Object.fromEntries(sortedEntries));
    }

    function isLocalhost() {
        return ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
    }

    function shouldUseSecureAttribute(secure) {
        if (!secure) {
            return false;
        }

        if (window.location.protocol === "https:") {
            return true;
        }

        return !isLocalhost();
    }

    function buildCookieAttributes(options, includeExpiryReset) {
        const attributes = [];
        const normalizedOptions = options ?? {};

        if (includeExpiryReset) {
            attributes.push("expires=Thu, 01 Jan 1970 00:00:00 GMT");
            attributes.push("max-age=0");
        } else {
            if (normalizedOptions.max_age !== undefined && normalizedOptions.max_age !== null) {
                attributes.push(`max-age=${normalizedOptions.max_age}`);
            }

            if (normalizedOptions.expires) {
                attributes.push(
                    `expires=${new Date(normalizedOptions.expires).toUTCString()}`
                );
            }
        }

        if (normalizedOptions.path) {
            attributes.push(`path=${normalizedOptions.path}`);
        }

        if (normalizedOptions.domain) {
            attributes.push(`domain=${normalizedOptions.domain}`);
        }

        if (shouldUseSecureAttribute(normalizedOptions.secure)) {
            attributes.push("secure");
        }

        if (normalizedOptions.samesite) {
            attributes.push(`samesite=${normalizedOptions.samesite}`);
        }

        return attributes;
    }

    function setCookie(name, value, options) {
        const encodedName = encodeURIComponent(name);
        const encodedValue = encodeURIComponent(value);
        const attributes = buildCookieAttributes(options, false);

        document.cookie = [`${encodedName}=${encodedValue}`, ...attributes].join("; ");
    }

    function deleteCookie(name, options) {
        const encodedName = encodeURIComponent(name);
        const attributes = buildCookieAttributes(options, true);

        document.cookie = [`${encodedName}=`, ...attributes].join("; ");
    }

    export default function (component) {
        const { data, setStateValue } = component;

        const operations = data?.operations ?? [];
        let lastProcessedOperationId = data?.last_processed_operation_id ?? 0;

        operations.forEach((operation) => {
            if (operation.type === "set") {
                setCookie(operation.name, operation.value, operation.options);
            } else if (operation.type === "delete") {
                deleteCookie(operation.name, operation.options);
            }

            lastProcessedOperationId = Math.max(
                lastProcessedOperationId,
                operation.id ?? lastProcessedOperationId
            );
        });

        const snapshot = parseCookies();

        setStateValue("ready", true);
        setStateValue("snapshot_json", serializeSnapshot(snapshot));
        setStateValue("last_processed_operation_id", lastProcessedOperationId);

        return () => {};
    }
    """,
)


def _state_key(component_key: str) -> str:
    return f"{component_key}__cookie_manager_state"


def _validate_cookie_name(name: str) -> None:
    if not name:
        raise StreamlitAPIException("Cookie names must not be empty.")

    if any(character.isspace() for character in name) or "=" in name or ";" in name:
        raise StreamlitAPIException("Cookie names must not contain whitespace, '=' or ';'.")


def _validate_cookie_value(name: str, value: str) -> None:
    if not isinstance(value, str):
        raise StreamlitAPIException("Cookie values must be strings.")

    encoded_size = len(quote(name, safe="")) + 1 + len(quote(value, safe=""))
    if encoded_size > _MAX_COOKIE_SIZE_BYTES:
        raise StreamlitAPIException("Cookies must be smaller than approximately 4 KB.")


def _normalize_max_age(max_age: int | timedelta | None) -> int | None:
    if max_age is None:
        return None

    if isinstance(max_age, timedelta):
        return int(max_age.total_seconds())

    if isinstance(max_age, int):
        return max_age

    raise StreamlitAPIException("`max_age` must be an int number of seconds or a timedelta.")


def _normalize_samesite(
    samesite: Literal["strict", "lax", "none"] | None,
) -> str | None:
    if samesite is None:
        return None

    normalized = samesite.lower()
    if normalized not in _VALID_SAMESITE_VALUES:
        raise StreamlitAPIException("`samesite` must be one of 'strict', 'lax', or 'none'.")

    return normalized


def _serialize_options(
    *,
    max_age: int | timedelta | None = None,
    expires: datetime | None = None,
    path: str = "/",
    domain: str | None = None,
    secure: bool = True,
    httponly: bool = False,
    samesite: Literal["strict", "lax", "none"] | None = "lax",
) -> dict[str, str | int | bool | None]:
    if httponly:
        raise StreamlitAPIException("HttpOnly cookies cannot be managed from a browser-side component.")

    normalized_options = {
        "max_age": _normalize_max_age(max_age),
        "expires": expires.isoformat() if expires else None,
        "path": path,
        "domain": domain,
        "secure": secure,
        "samesite": _normalize_samesite(samesite),
    }
    return {key: value for key, value in normalized_options.items() if value is not None}


class CookieManager(MutableMapping[str, str]):
    """A dict-like interface for managing browser cookies.

    The CookieManager provides read/write access to browser cookies through
    a MutableMapping interface. Cookies can be accessed like a dictionary
    or through explicit `set()` and `delete()` methods for fine-grained control.

    Note:
        This component can only manage JavaScript-accessible cookies.
        HttpOnly cookies are not supported.
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

        # Use st._event container to avoid adding any visual space to the UI
        with st._event:
            self._result = _COOKIE_MANAGER_COMPONENT(
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
        """Check if the cookie manager has synced with the browser.

        Returns:
            True if cookies have been loaded from the browser, False otherwise.
        """
        return self._ready

    def set(
        self,
        name: str,
        value: str,
        *,
        max_age: int | timedelta | None = None,
        expires: datetime | None = None,
        path: str = "/",
        domain: str | None = None,
        secure: bool = True,
        httponly: bool = False,
        samesite: Literal["strict", "lax", "none"] = "lax",
    ) -> None:
        """Set a cookie with the given name and value.

        Args:
            name: The cookie name.
            value: The cookie value (must be a string).
            max_age: Cookie lifetime in seconds or as a timedelta.
            expires: Absolute expiration datetime.
            path: Cookie path (default "/").
            domain: Cookie domain.
            secure: Whether the cookie requires HTTPS (default True).
            httponly: Not supported - will raise an error if True.
            samesite: SameSite attribute ("strict", "lax", or "none").
        """
        _validate_cookie_name(name)
        _validate_cookie_value(name, value)

        self._queue_operation(
            operation_type="set",
            name=name,
            value=value,
            options=_serialize_options(
                max_age=max_age,
                expires=expires,
                path=path,
                domain=domain,
                secure=secure,
                httponly=httponly,
                samesite=samesite,
            ),
        )

    def delete(
        self,
        name: str,
        *,
        path: str = "/",
        domain: str | None = None,
        secure: bool = True,
        samesite: Literal["strict", "lax", "none"] = "lax",
    ) -> None:
        """Delete a cookie by name.

        Args:
            name: The cookie name to delete.
            path: Cookie path (must match the path used when setting).
            domain: Cookie domain (must match the domain used when setting).
            secure: Whether the cookie requires HTTPS.
            samesite: SameSite attribute.
        """
        _validate_cookie_name(name)

        self._queue_operation(
            operation_type="delete",
            name=name,
            value=None,
            options=_serialize_options(
                path=path,
                domain=domain,
                secure=secure,
                samesite=samesite,
            ),
        )

    def _queue_operation(
        self,
        *,
        operation_type: Literal["set", "delete"],
        name: str,
        value: str | None,
        options: dict[str, str | int | bool | None],
    ) -> None:
        operation_id = self._store["next_operation_id"]
        self._store["next_operation_id"] += 1
        self._store["pending_operations"].append(
            {
                "id": operation_id,
                "type": operation_type,
                "name": name,
                "value": value,
                "options": options,
            }
        )

    def __getitem__(self, key: str) -> str:
        return self._snapshot[key]

    def __setitem__(self, key: str, value: str) -> None:
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
def cookie_manager(*, key: str = "cookie_manager") -> CookieManager:
    """Create a cookie manager to read and write browser cookies from Python.

    This component provides a dict-like interface for managing browser cookies.
    The manager must be rendered in your app (it creates a hidden component)
    and requires a rerun to sync cookies from the browser on first load.

    The returned ``CookieManager`` implements Python's ``MutableMapping`` protocol,
    so you can use it like a dictionary:

    - ``manager["name"]`` - get a cookie value (raises ``KeyError`` if not found)
    - ``manager.get("name", "default")`` - get with a default value
    - ``manager["name"] = "value"`` - set a cookie (with default options)
    - ``del manager["name"]`` - delete a cookie
    - ``"name" in manager`` - check if a cookie exists
    - ``len(manager)`` - count of cookies
    - ``dict(manager)`` - convert to a regular dict
    - ``manager.keys()``, ``manager.values()``, ``manager.items()`` - iterate

    For fine-grained control over cookie attributes (expiration, path, domain,
    secure, samesite), use the explicit ``manager.set()`` and ``manager.delete()``
    methods instead of dict-style assignment.

    Args:
        key: A unique key for this component instance. Defaults to "cookie_manager".
            Use different keys if you need multiple independent cookie managers.

    Returns:
        A CookieManager instance that provides dict-like access to cookies.

    Note:
        - Call ``manager.ready()`` to check if cookies have synced from the browser
        - Use ``st.stop()`` on first load while waiting for sync
        - This can only manage JavaScript-accessible cookies (not HttpOnly)
        - After setting/deleting cookies, call ``st.rerun()`` to see changes

    Example:

        ```python
        manager = cookie_manager()
        if not manager.ready():
            st.stop()  # Wait for browser sync
        theme = manager.get("theme", "light")
        if st.button("Use dark theme"):
            manager["theme"] = "dark"
            st.rerun()
        ```

    Example with custom cookie options:

        ```python
        manager = cookie_manager()
        if manager.ready():
            # Set cookie with 1-hour expiration
            manager.set("session", "abc123", max_age=3600, secure=True)
        ```
    """
    return CookieManager(key=key)


def example() -> None:
    """Example usage of the cookie_manager component."""
    st.info("This component can only manage JavaScript-accessible cookies. HttpOnly cookies are not supported.")

    manager = cookie_manager(key="demo_cookie_manager")

    if not manager.ready():
        st.info("Syncing cookies from browser. The app will be ready on the next rerun.")
        st.stop()

    st.subheader("Current cookies")
    st.json(dict(manager))

    get_col, set_col, delete_col = st.columns(3)

    with get_col:
        st.markdown("**Get cookie**")
        cookie_name = st.text_input("Cookie name", key="cookie_get_name")
        if st.button("Read cookie", key="cookie_get_button"):
            st.write(manager.get(cookie_name))

    with set_col:
        st.markdown("**Set cookie**")
        set_name = st.text_input("Name", key="cookie_set_name")
        set_value = st.text_input("Value", key="cookie_set_value")
        set_max_age = st.number_input(
            "Max age (seconds)",
            min_value=0,
            value=86400,
            step=60,
            key="cookie_set_max_age",
        )
        set_secure = st.checkbox("Secure", value=False, key="cookie_set_secure")
        set_samesite = st.selectbox(
            "SameSite",
            ["lax", "strict", "none"],
            index=0,
            key="cookie_set_samesite",
        )
        if st.button("Write cookie", key="cookie_set_button"):
            selected_samesite = cast(
                "Literal['strict', 'lax', 'none']",
                "lax" if set_samesite is None else set_samesite,
            )

            manager.set(
                set_name,
                set_value,
                max_age=int(set_max_age),
                secure=set_secure,
                samesite=selected_samesite,
            )
            st.rerun()

    with delete_col:
        st.markdown("**Delete cookie**")
        delete_name = st.text_input("Cookie to delete", key="cookie_delete_name")
        if st.button("Delete cookie", key="cookie_delete_button"):
            manager.delete(delete_name)
            st.rerun()

    st.subheader("Basic usage")
    st.code(
        """
manager = cookie_manager()

if not manager.ready():
    st.stop()  # Wait for browser sync

# Dict-like access
theme = manager.get("theme", "light")
st.write(f"Current theme: {theme}")

if st.button("Use dark theme"):
    manager["theme"] = "dark"
    st.rerun()

# Or use set() for more control
manager.set("session_id", "abc123", max_age=3600, secure=True)
""".strip(),
        language="python",
    )


__title__ = "Cookie Manager"
__desc__ = "Read and write browser cookies from Python using a dict-like interface."
__icon__ = "🍪"
__examples__ = [example]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 3, 24)
