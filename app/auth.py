"""
Authentication utilities for the Sentry Test Application.
"""


def get_current_user(session):
    """Return the current user's ID from the session."""
    return session.user.id
