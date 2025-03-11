from typing import Any, Callable, Dict, Literal, Optional

import streamlit as st

from .. import extra


@extra
def floating_button(
    label: str,
    key: Optional[str] = None,
    help: Optional[str] = None,
    on_click: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    *,
    type: Literal["primary", "secondary"] = "secondary",
    icon: Optional[str] = None,
    disabled: bool = False,
):
    """
    Display a floating action button that stays fixed at the bottom right corner of the
    screen.

    This is similar to st.button but creates a button that floats above the content and
    remains visible even when scrolling. Only one floating button can be shown at a time.

    Parameters
    ----------
    label : str
        A short label explaining to the user what this button is for. The label can
        optionally contain GitHub-flavored Markdown.
    key : str or int, optional
        An optional string or integer to use as the unique key for the widget.
        If this is omitted, a key will be generated for the widget based on its content.
    help : str, optional
        A tooltip that gets displayed when the button is hovered over.
    on_click : callable, optional
        An optional callback invoked when this button is clicked.
    args : tuple, optional
        An optional tuple of args to pass to the callback.
    kwargs : dict, optional
        An optional dict of kwargs to pass to the callback.
    type : str, optional
        The button type, either "primary" or "secondary" (default: "secondary").
        Note that "tertiary" is not supported for floating buttons.
    icon : str, optional
        An optional emoji or Material icon to display next to the button label.
        For Material icons, use the format ":material/icon_name:".
    disabled : bool, optional
        An optional boolean that disables the button if set to True (default: False).

    Returns
    -------
    bool
        True if the button was clicked on the last run of the app, False otherwise.

    Examples
    --------
    >>> if st.floating_button(":material/chat:"):
    ...     st.write("Chat button clicked!")
    >>>
    >>> if st.floating_button("Add", icon=":material/add:"):
    ...     st.write("Add button clicked!")
    """
    # Validate type parameter
    if type not in ["primary", "secondary"]:
        raise ValueError(
            f"Invalid type: {type}. Must be 'primary' or 'secondary', 'tertiary' is not "
            "supported for floating buttons. Using 'secondary'."
        )

    # Generate a unique key if none is provided
    if key is None:
        key = "fab"

    # Create CSS for the floating button
    st.markdown(
        f"""
        <style>
            .st-key-{key} button {{
                position: fixed;
                bottom: 3.5rem;
                right: 3.5rem;
                min-width: 3.5rem;
                min-height: 3.5rem;
                padding: 0.875rem;
                box-shadow: rgba(0, 0, 0, 0.16) 0px 4px 16px;
                z-index: 999;
                border-radius: 1rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Create the button
    return st.button(
        label=label,
        key=key,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        type=type,
        disabled=disabled,
        help=help,
        icon=icon,
    )


def example():
    """Example usage of the floating_button function."""
    st.title("Floating action button demo")
    st.write("See in the bottom right corner :wink:")

    # Initialize chat messages in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]

    # Chat dialog using decorator
    @st.dialog("Chat Support", width="large")
    def chat_dialog():
        # Create a container for chat messages with fixed height
        messages_container = st.container(height=400, border=False)

        # Display messages in the container
        with messages_container:
            # Display all messages from session state
            for message in st.session_state.messages:
                st.chat_message(message["role"]).write(message["content"])

        # Chat input (placed below the messages container in the UI)
        user_input = st.chat_input("Type a message...")

        # Handle new user input
        if user_input:
            messages_container.chat_message("user").write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Add bot response to chat history
            messages_container.chat_message("assistant").write(
                "Thanks for your message! This is a demo response."
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Thanks for your message! This is a demo response.",
                }
            )

    # Handle FAB button click to open the dialog
    if floating_button(":material/chat: Chat"):
        chat_dialog()


__title__ = "Floating button"
__desc__ = """A button that stays fixed at the bottom right corner of the screen.
Perfect for creating action buttons that are always accessible to users, such as chat
interfaces."""
__icon__ = "🔘"
__examples__ = [example]
__author__ = "Johannes Rieke"
__experimental_playground__ = True
