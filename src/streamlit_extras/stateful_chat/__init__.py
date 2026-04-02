from __future__ import annotations

import inspect
import time
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import date
from typing import TYPE_CHECKING, Any, Literal

import streamlit as st
from streamlit.errors import StreamlitAPIException
from typing_extensions import Required, TypedDict

from .. import extra

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator
    from streamlit.elements.lib.image_utils import AtomicImage

SpecType = int | Sequence[int | float]

# Context variable to track the active chat container
_active_chat_container: ContextVar[Any] = ContextVar("active_chat_container", default=None)


def _streaming_write(*args: Any, unsafe_allow_html: bool = False, **kwargs: Any) -> list[Any]:
    """Internal streaming write implementation for stateful chat.

    Returns:
        list[Any]: A list of written content items.
    """
    if not args:
        return []

    written_content: list[Any] = []
    string_buffer: list[str] = []

    def flush_buffer() -> None:
        if string_buffer:
            text_content = " ".join(string_buffer)
            text_container = st.empty()
            text_container.markdown(text_content)
            written_content.append(text_content)
            string_buffer[:] = []

    for arg in args:
        if isinstance(arg, str):
            string_buffer.append(arg)
        elif callable(arg) or inspect.isgenerator(arg):
            flush_buffer()
            if inspect.isgeneratorfunction(arg) or inspect.isgenerator(arg):
                stream_container = None
                streamed_response = ""

                def flush_stream_response() -> None:
                    nonlocal streamed_response, stream_container
                    if streamed_response and stream_container:
                        stream_container.write(
                            streamed_response,
                            unsafe_allow_html=unsafe_allow_html,
                            **kwargs,
                        )
                        written_content.append(streamed_response)
                        stream_container = None
                        streamed_response = ""

                generator = arg() if inspect.isgeneratorfunction(arg) else arg
                for chunk in generator:
                    if isinstance(chunk, str):
                        first_text = False
                        if not stream_container:
                            stream_container = st.empty()
                            first_text = True
                        streamed_response += chunk
                        stream_container.write(
                            streamed_response + ("" if first_text else " ▌"),
                            unsafe_allow_html=unsafe_allow_html,
                            **kwargs,
                        )
                    elif callable(chunk):
                        flush_stream_response()
                        chunk()
                        written_content.append(chunk)
                    else:
                        flush_stream_response()
                        st.write(chunk, unsafe_allow_html=unsafe_allow_html, **kwargs)
                        written_content.append(chunk)
                flush_stream_response()
            else:
                return_value = arg()
                written_content.append(arg)
                if return_value is not None:
                    flush_buffer()
                    st.write(return_value, unsafe_allow_html=unsafe_allow_html, **kwargs)
        else:
            flush_buffer()
            st.write(arg, unsafe_allow_html=unsafe_allow_html, **kwargs)
            written_content.append(arg)
    flush_buffer()
    return written_content


class ChatMessage(TypedDict):
    author: Required[str]
    avatar: Required[str | AtomicImage | None]
    content: Required[list[Any]]


def _active_dg() -> Any:
    return _active_chat_container.get()


def _display_message(
    name: str,
    *args: Any,
    avatar: str | AtomicImage | None = None,
) -> list[Any]:
    with st.chat_message(name, avatar=avatar):
        return _streaming_write(*args)


@extra
def add_message(
    name: str,
    *args: Any,
    avatar: str | AtomicImage | None = None,
) -> None:
    """Adds a chat message to the chat container.

    This command can only be used inside the `chat` container. The message
    will be displayed in the UI and added to the chat history so that the same
    message will be automatically displayed on reruns.

    Args:
        name (Literal["user", "assistant"] | str):
            The name of the message author. Can be "user" or "assistant" to
            enable preset styling and avatars.
            Currently, the name is not shown in the UI but is only set as an
            accessibility label. For accessibility reasons, you should not use
            an empty string.
        avatar (str | AtomicImage | None, optional):
            The avatar shown next to the message. Can be anything that is supported by
            the `avatar` parameter of `st.chat_message`. Defaults to None.
        *args (Any):
            The content of the message. This can be any number of elements that are supported by
            `st.write` as well as generator functions to stream content to the UI.

    Raises:
        StreamlitAPIException: If called outside of a `chat` container.
    """
    active_dg = _active_dg()

    if not hasattr(active_dg, "chat_history"):
        raise StreamlitAPIException("The `add_message` command can only be used inside a `chat` container.")

    # Write to the active container (new_messages_container)
    with active_dg:
        displayed_elements = _display_message(name, *args, avatar=avatar)

    active_dg.chat_history.append(
        ChatMessage(
            author=name,
            avatar=avatar,
            content=displayed_elements,
        )
    )


@extra
@contextmanager
def chat(key: str = "chat_messages") -> Generator[DeltaGenerator, None, None]:
    """Insert a stateful chat container into your app.

    This chat container automatically keeps track of the chat history when you use
    the `add_message` command to add messages to the chat.

    Args:
        key (str, optional): The key that is used to keep track of the chat history in session state.
            Defaults to "chat_messages".

    Yields:
        DeltaGenerator: The chat container that can be used together with `add_message` to
            automatically keep track of the chat history.
    """

    chat_container = st.container()

    if key not in st.session_state:
        st.session_state[key] = []
    chat_history: list[ChatMessage] = st.session_state[key]

    with chat_container:
        # Display existing messages from history
        for message in chat_history:
            _display_message(message["author"], *message["content"], avatar=message["avatar"])

        # Create a container for new messages BEFORE yielding
        # This ensures new messages appear above any content (like chat_input)
        # that the user adds in the yielded block
        new_messages_container = st.container()

    new_messages_container.chat_history = chat_history  # type: ignore

    # Set the active chat container for add_message to use
    token = _active_chat_container.set(new_messages_container)
    try:
        with chat_container:
            yield chat_container
    finally:
        _active_chat_container.reset(token)


def example() -> None:
    with chat(key="my_chat"):
        if prompt := st.chat_input():
            add_message("user", prompt, avatar="🧑‍💻")

            def stream_echo() -> Generator[str, None, None]:
                for word in prompt.split():
                    yield word + " "
                    time.sleep(0.15)

            add_message("assistant", "Echo: ", stream_echo, avatar="🦜")


__title__ = "Stateful Chat"
__desc__ = "A chat container that automatically keeps track of the chat history."
__icon__ = "💬"
__examples__ = {
    example: [chat, add_message],
}
__author__ = "Lukas Masuch"
__created_at__ = date(2023, 8, 1)
__playground__ = False
