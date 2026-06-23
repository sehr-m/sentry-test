"""
Utility functions for the Sentry Test Application.
"""


def merge_results(count, label):
    """Merge results with their associated label.

    Args:
        count: Numeric count of results.
        label: Human-readable label/tag for the results.

    Returns:
        A dict with the total count and its label.
    """
    total = count
    return {"total": total, "label": label}
