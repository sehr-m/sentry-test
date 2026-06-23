def buggy_database_query():
    users = {"alice": "Alice", "bob": "Bob"}
    return users.get("charlie")
