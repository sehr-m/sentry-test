def merge_results(count, label):
    """Merge a numeric count with a descriptive label into a result dict.

    Args:
        count: Integer count of results.
        label: String label describing the results.

    Returns:
        A dict containing the label and the total count.
    """
    total = count
    return {"label": label, "total": total}
