import json
import uuid
from typing import Any

import streamlit as st
from streamlit_js import st_js_blocking

from .. import extra

KEY_PREFIX = "st_localstorage_"


class StLocalStorage:
    """An Dict-like wrapper around browser local storage.

    Values are stored JSON encoded."""

    def __init__(self):
        # Keep track of a UUID for each key to enable reruns
        if "_ls_unique_keys" not in st.session_state:
            st.session_state["_ls_unique_keys"] = {}

    def __getitem__(self, key: str) -> Any:
        if key not in st.session_state["_ls_unique_keys"]:
            st.session_state["_ls_unique_keys"][key] = str(uuid.uuid4())
        code = f"""
        // The UUID changes on save, which causes this to rerun and update
        console.debug('{st.session_state["_ls_unique_keys"][key]}');
        return JSON.parse(localStorage.getItem('{KEY_PREFIX + key}'));
        """
        result = st_js_blocking(code)
        if result:
            return json.loads(result)
        return None

    def __setitem__(self, key: str, value: Any) -> None:
        value = json.dumps(value, ensure_ascii=False)
        st.session_state["_ls_unique_keys"][key] = str(uuid.uuid4())
        code = f"localStorage.setItem('{KEY_PREFIX + key}', JSON.stringify('{value}'));"
        return st_js_blocking(code)

    def __delitem__(self, key: str) -> None:
        st.session_state["_ls_unique_keys"][key] = str(uuid.uuid4())
        code = f"localStorage.removeItem('{KEY_PREFIX + key}');"
        return st_js_blocking(code)

    def __contains__(self, key: str) -> bool:
        val = self.__getitem__(key)
        if val:
            return True
        return False


@extra
def local_storage() -> StLocalStorage:
    """
    Create a dict-like store backed by browser localStorage.

    Key, value pairs stored in local_storage will persist across user sessions in the
    same browser. See:
    https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

    This extra is built on streamlit-js:
    https://pypi.org/project/streamlit-js/

    **NOTE:** Storing data on an app viewer's machine may have privacy and compliance
    implications for your app. Be sure to take that into account with any usage.

    **KNOWN ISSUE:** Calls to local_storage can trigger extra stop() and rerun() calls
    unexpectedly. For example, in the following, the last line will not run
    consistently:

    ```python
    ls = local_storage()
    if st.button("Save"):
        ls["my_key"] =  "some_val"
        print("This won't execute")
    ```
    """

    # Hide the JS iframes
    st.html(
        """
        <style>
            .element-container:has(iframe[height="0"]) {
                display: none;
            }
        </style>
    """
    )

    return StLocalStorage()


def example():
    st.title("local_storage basic example")

    "Any values you save will be available after leaving / refreshing the tab"

    ls = local_storage()

    key = st.text_input("Key")
    value = st.text_input("Value")
    if st.button("Save"):
        ls[key] = value

    if key:
        f"Current value of {key} is:"
        st.write(ls[key])

    if st.button("Delete"):
        del ls[key]
        st.rerun()


__title__ = "Local Storage"
__desc__ = "Use browser localStorage across a user's sessions with a dict-like API."
__icon__ = "✉️"
__examples__ = [example]
__author__ = "Joshua Carroll"
__experimental_playground__ = False
