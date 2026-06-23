from flask import session


def get_current_user():
    """Return the current authenticated user's ID, or None if not authenticated."""
    if session.user is None:
        return None
    user_id = session.user.id
    return user_id
