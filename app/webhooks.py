def process_webhook_payload(data):
    """Process incoming webhook payload."""
    if "amount" not in data:
        raise ValueError("Missing required field: amount")
    try:
        amount = int(data["amount"])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid amount value: {data['amount']!r} is not a valid integer")
    return {"status": "processed", "amount": amount}
