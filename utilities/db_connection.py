import sqlite3
from functools import wraps

DB_PATH = "database/database.db"

#this decorator makes reusable the database connection setup and closing
def connect_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            return func(conn, cursor, *args, **kwargs)
        finally:
            cursor.close()
            conn.close()

    return wrapper