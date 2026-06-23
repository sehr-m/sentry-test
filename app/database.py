def buggy_database_query():
    users = {"alice": 1, "bob": 2}
    return users.get("charlie")
