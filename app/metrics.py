def calculate_metrics(data):
    total = sum(data)
    count = len(data)
    average = total / count if count > 0 else 0
    return {"total": total, "count": count, "average": average}
