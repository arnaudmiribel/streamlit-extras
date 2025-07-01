# extras/streamlit_notify/__init__.py
from streamlit_notify import (
    add_notifications,
    balloons_stn,
    clear_notifications,
    create_notification,
    error_stn,
    exception_stn,
    get_notification_queue,
    get_notifications,
    has_notifications,
    info_stn,
    notify,
    remove_notifications,
    snow_stn,
    success_stn,
    toast_stn,
    warning_stn,
)

from .. import extra


def example_status_elements():
    from streamlit_notify import (
        balloons_stn,
        error_stn,
        exception_stn,
        info_stn,
        notify,
        snow_stn,
        success_stn,
        toast_stn,
        warning_stn,
    )

    # Display various status elements as examples
    # Call each status element exactly like in Streamlit
    toast_stn("🔔 Toast Notification Example")
    balloons_stn()
    snow_stn()
    success_stn("✅ Success Notification Example")
    info_stn("ℹ️ Info Notification Example")
    error_stn("❌ Error Notification Example")
    warning_stn("⚠️ Warning Notification Example")
    exception_stn("🐛 Exception Notification Example")

    notify()  # Display all queued notifications


def example_priority():
    from streamlit_notify import notify, toast_stn

    # Display a toast notification with a custom priority
    toast_stn("🔔 Toast Notification with Custom Priority (5)", priority=5)
    toast_stn("🔔 Toast Notification with Custom Priority (1)", priority=1)

    # Display a notification with with higher priority first
    notify()

    # Display all notifications with a priority of 5 or higher
    notify(priority=5)

    # Display all notifications with a priority of 5 or lower
    # Other options: "ge", "gt", "le", "lt", "eq"
    notify(priority=5, priority_type="le")


def example_use():
    import streamlit as st
    from streamlit_notify import notify, toast_stn

    notify()

    if st.button("Show Toast Notification"):
        toast_stn("🔔 Toast Notification Example")
        st.rerun()


def example_notify():
    from streamlit_notify import notify

    # show all queued notifications
    notify()

    # By default notify will remove notifications after displaying them.
    # If you want to keep them in the queue, you can pass `remove=False`
    notify(remove=False)

    # Show queued toast notifications
    notify(notification_type="toast")

    # show queued success and toast notifications
    notify(notification_type=["success", "toast"])


def example_get_notification_queue():
    from streamlit_notify import get_notification_queue

    # Get the toast notification queue
    # With this you can access the queue directly, and manipulate it as needed
    get_notification_queue(notification_type="toast")

    """
    The notification queue supports standard list operations:

        append(item) - Add notification to queue
        extend(items) - Add multiple notifications
        pop(index) - Remove and return notification at index
        get(index) - Get notification without removing it
        remove(item) - Remove specific notification
        clear() - Remove all notifications
        has_items() - Check if queue has notifications
        is_empty() - Check if queue is empty
        contains(item) - Check if notification exists in queue
        get_all() - Get all notifications
        size() - Get number of notifications

    """


def example_get_notifications():
    from streamlit_notify import get_notifications

    # Get all toast notifications
    get_notifications(notification_type="toast")

    # Get all success and toast notifications
    get_notifications(notification_type=["toast", "success"])

    # Get all notifications of all types
    get_notifications()

    """
    Notification:

        Attributes:

            base_widget: Callable[..., Any]
            args: OrderedDict[str, Any]
            priority: int = 0
            data: Any = None

        Properties:
            name: str - Name of the notification type (e.g., 'toast')

        Methods:
            notify: Display the notification
    """


def example_has_notifications():
    from streamlit_notify import has_notifications

    # Check if there are any notifications in the queue
    has_notifications()

    # Check if there are any toast notifications
    has_notifications("toast")

    # Check if there are any success or toast notifications
    has_notifications(["success", "toast"])


def example_create_add_remove_notifications():
    from streamlit_notify import (
        add_notifications,
        create_notification,
        remove_notifications,
    )

    # Get the current toast notifications
    notification = create_notification(
        body="🌟 Custom Toast Notification",
        icon="⭐",
        priority=4,
        notification_type="toast",
    )

    # Add a new notification to the queue
    # Automatically adds to the toast queue
    add_notifications(notification)

    # can also add multiple notifications at once
    # Adds two of the same notification
    add_notifications([notification, notification])

    # Remove a specific notification from the queue
    # Automatically removes from the toast queue (first match)
    remove_notifications(notification)

    # Can also remove multiple notifications at once
    # Removes two of the same notification
    remove_notifications([notification, notification])


def example_clear_notifications():
    from streamlit_notify import clear_notifications

    # Clear all notifications from the queue
    clear_notifications()

    # Clear only toast notifications
    clear_notifications(notification_type="toast")

    # Clear success and toast notifications
    clear_notifications(notification_type=["success", "toast"])


toast_stn = extra(toast_stn)
balloons_stn = extra(balloons_stn)
snow_stn = extra(snow_stn)
success_stn = extra(success_stn)
info_stn = extra(info_stn)
error_stn = extra(error_stn)
warning_stn = extra(warning_stn)
exception_stn = extra(exception_stn)
notify = extra(notify)
get_notifications = extra(get_notifications)
get_notification_queue = extra(get_notification_queue)
create_notification = extra(create_notification)
has_notifications = extra(has_notifications)
remove_notifications = extra(remove_notifications)
clear_notifications = extra(clear_notifications)
add_notifications = extra(add_notifications)

__title__ = "Streamlit Notify"
__desc__ = (
    "Queue and display Streamlit Status Elements like toasts, balloons, and snowflakes."
)
__icon__ = "🔔"
__examples__ = {  # type: ignore
    example_status_elements: [
        toast_stn,
        balloons_stn,
        snow_stn,
        success_stn,
        info_stn,
        error_stn,
        warning_stn,
        exception_stn,
    ],
    example_notify: [notify],
    example_get_notification_queue: [get_notification_queue],
    example_get_notifications: [get_notifications],
    example_has_notifications: [has_notifications],
    example_create_add_remove_notifications: [
        create_notification,
        add_notifications,
        remove_notifications,
    ],
    example_clear_notifications: [clear_notifications],
}
__author__ = "Patrick Garrett"
__pypi_name__ = "streamlit-notify"
__package_name__ = "streamlit_notify"
__github_repo__ = "https://github.com/pgarrett-scripps/Streamlit_Notify"
__streamlit_cloud_url__ = "https://st-notify.streamlit.app/"
__experimental_playground__ = False
