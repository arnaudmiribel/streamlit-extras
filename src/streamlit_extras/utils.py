"""Internal utility functions for streamlit-extras."""

from urllib.parse import urlparse


def is_url(s: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        s: The string to check.

    Returns:
        True if the string is a valid URL with scheme and netloc, False otherwise.
    """
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
