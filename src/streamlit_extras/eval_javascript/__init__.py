"""Evaluate JavaScript expressions in the browser and return results to Python.

A Streamlit Custom Component v2 (CCv2) that evaluates a JavaScript expression
in the browser and returns the result to Python. The component itself is hidden.
"""

from datetime import date
from typing import Any

import streamlit as st
import streamlit.components.v2

from streamlit_extras import extra

_JAVASCRIPT_EVAL_COMPONENT = st.components.v2.component(
    name="streamlit_extras.eval_javascript",
    html="<div aria-hidden='true'></div>",
    js="""
    const latestRequestIds = new WeakMap();
    const activeRequestIds = new WeakMap();

    export default function (component) {
        const { data, parentElement, setStateValue } = component;

        const expression = data?.expression ?? "";
        const requestId = data?.request_id ?? 0;
        const completedRequestId = data?.completed_request_id ?? -1;
        const currentStatus = data?.status ?? "idle";
        const currentResult = data?.result ?? null;
        const currentError = data?.error ?? null;

        latestRequestIds.set(parentElement, requestId);

        function serializeValue(value) {
            if (value === undefined || value === null) {
                return null;
            }

            if (typeof value === "bigint") {
                return value.toString();
            }

            if (value instanceof Date) {
                return value.toISOString();
            }

            if (typeof value === "function" || typeof value === "symbol") {
                return String(value);
            }

            if (value instanceof Error) {
                return {
                    name: value.name,
                    message: value.message,
                    stack: value.stack ?? null,
                };
            }

            if (Array.isArray(value)) {
                return value.map(serializeValue);
            }

            if (typeof value === "object") {
                if (value instanceof URL) {
                    return value.toString();
                }

                try {
                    return JSON.parse(
                        JSON.stringify(value, (_key, nestedValue) => {
                            if (typeof nestedValue === "bigint") {
                                return nestedValue.toString();
                            }

                            if (
                                typeof nestedValue === "function" ||
                                typeof nestedValue === "symbol"
                            ) {
                                return String(nestedValue);
                            }

                            if (nestedValue instanceof URL) {
                                return nestedValue.toString();
                            }

                            if (nestedValue instanceof Map) {
                                return Object.fromEntries(nestedValue);
                            }

                            if (nestedValue instanceof Set) {
                                return Array.from(nestedValue);
                            }

                            if (nestedValue instanceof Error) {
                                return {
                                    name: nestedValue.name,
                                    message: nestedValue.message,
                                    stack: nestedValue.stack ?? null,
                                };
                            }

                            return nestedValue;
                        })
                    );
                } catch (error) {
                    return String(value);
                }
            }

            return value;
        }

        function serializeError(error) {
            return {
                name: error?.name ?? "Error",
                message: error?.message ?? String(error),
                stack: error?.stack ?? null,
            };
        }

        if (!expression.trim()) {
            activeRequestIds.delete(parentElement);

            if (
                currentStatus !== "idle" ||
                currentResult !== null ||
                currentError !== null ||
                completedRequestId !== requestId
            ) {
                setStateValue("status", "idle");
                setStateValue("result", null);
                setStateValue("error", null);
                setStateValue("completed_request_id", requestId);
            }

            return () => {};
        }

        if (completedRequestId === requestId) {
            return () => {};
        }

        if (activeRequestIds.get(parentElement) === requestId) {
            return () => {};
        }

        activeRequestIds.set(parentElement, requestId);
        setStateValue("status", "running");

        Promise.resolve()
            .then(() => eval(expression))
            .then((rawResult) => {
                if (latestRequestIds.get(parentElement) !== requestId) {
                    return;
                }

                const serializedResult = serializeValue(rawResult);

                activeRequestIds.delete(parentElement);
                setStateValue("result", serializedResult);
                setStateValue("error", null);
                setStateValue("status", "success");
                setStateValue("completed_request_id", requestId);
            })
            .catch((error) => {
                if (latestRequestIds.get(parentElement) !== requestId) {
                    return;
                }

                const serializedError = serializeError(error);

                activeRequestIds.delete(parentElement);
                setStateValue("result", null);
                setStateValue("error", serializedError);
                setStateValue("status", "error");
                setStateValue("completed_request_id", requestId);
            });

        return () => {
            if (latestRequestIds.get(parentElement) !== requestId) {
                activeRequestIds.delete(parentElement);
            }
        };
    }
    """,
)


@extra
def eval_javascript(expression: str, *, key: str) -> Any | None:
    """Evaluate a JavaScript expression in the browser and return the result.

    This component evaluates a JavaScript expression in the user's browser using
    `eval()` and returns the serialized result to Python. The component itself is
    invisible (zero-height).

    Args:
        expression: The JavaScript expression to evaluate. Can be synchronous or
            return a Promise for async evaluation.
        key: A unique key for this component instance. Required to track state
            across reruns.

    Returns:
        The result of the JavaScript expression, serialized to a Python-compatible
        value. Returns None while the expression is being evaluated or if the
        expression is empty.

    Note:
        - The expression is evaluated with browser-side JavaScript `eval()`
        - Supports async expressions (Promises are automatically awaited)
        - Complex objects are serialized (Maps become dicts, Sets become lists, etc.)
        - Errors are captured and can be accessed via session state

    Example:

        ```python
        user_agent = eval_javascript("window.navigator.userAgent", key="ua")
        if user_agent:
            st.write(f"Your browser: {user_agent}")
        ```
    """
    component_state = st.session_state.get(key, {})
    request_state_key = f"{key}__eval_javascript_request"
    request_state = st.session_state.get(
        request_state_key,
        {"expression": None, "request_id": 0},
    )

    if request_state["expression"] != expression:
        request_state = {
            "expression": expression,
            "request_id": request_state["request_id"] + 1,
        }
        st.session_state[request_state_key] = request_state

    request_id = request_state["request_id"]
    current_result = component_state.get("result")
    current_error = component_state.get("error")
    current_status = component_state.get("status", "idle")
    completed_request_id = component_state.get("completed_request_id", -1)

    # Use st._event container to avoid adding any visual space to the UI
    with st._event:
        _JAVASCRIPT_EVAL_COMPONENT(
            key=key,
            data={
                "expression": expression,
                "request_id": request_id,
                "result": current_result,
                "error": current_error,
                "status": current_status,
                "completed_request_id": completed_request_id,
            },
            default={
                "result": current_result,
                "error": current_error,
                "status": current_status,
                "completed_request_id": completed_request_id,
            },
            on_result_change=lambda: None,
            on_error_change=lambda: None,
            on_status_change=lambda: None,
            on_completed_request_id_change=lambda: None,
            width="stretch",
            height=0,
        )

    if completed_request_id != request_id:
        return None

    return current_result


def example() -> None:
    """Example usage of the eval_javascript component."""
    examples = {
        "User agent": "window.navigator.userAgent",
        "Window width": "window.innerWidth",
        "Location summary": "({ href: window.location.href, host: window.location.host })",
        "Async example": "Promise.resolve({ language: window.navigator.language })",
        "Thrown error": "(() => { throw new Error('Boom'); })()",
    }

    selected_example = st.selectbox("Example expression", list(examples))
    selected_expression = "window.navigator.userAgent" if selected_example is None else examples[selected_example]

    expression = st.text_area(
        "JavaScript expression",
        value=selected_expression,
        height=140,
        help="The expression is evaluated with browser-side JavaScript `eval(...)`.",
    )

    value = eval_javascript(expression, key="eval_javascript_demo")
    component_state = st.session_state.get("eval_javascript_demo", {})
    status = component_state.get("status", "idle")
    error = component_state.get("error")

    st.subheader("Python result")
    if status == "running":
        st.info("Evaluating in the browser...")
    elif error:
        error_name = error.get("name", "Error")
        error_message = error.get("message", "Unknown error")
        st.error(f"{error_name}: {error_message}")
        if error.get("stack"):
            st.code(error["stack"], language="text")
    else:
        st.write(value)


__title__ = "Eval JavaScript"
__desc__ = "Evaluate JavaScript expressions in the browser and return results to Python."
__icon__ = "🌐"
__examples__ = [example]
__author__ = "Lukas Masuch"
__created_at__ = date(2026, 3, 24)
