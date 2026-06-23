"""
Authentication utilities for the Sentry Test Application.
"""


def get_current_user(session):
    """Return the current user's ID from the session."""
    if session.user is None:
        return None
    return session.user.id
