def calculate_metrics(data):
    total = sum(data)
    count = len(data)
    average = total / count
    return {"total": total, "count": count, "average": average}
