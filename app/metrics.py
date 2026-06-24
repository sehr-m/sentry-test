def calculate_metrics(data):
    total = sum(data)
    count = len(data)
    if count == 0:
        return {"total": 0, "count": 0, "average": 0}
    average = total / count
    return {"total": total, "count": count, "average": average}
