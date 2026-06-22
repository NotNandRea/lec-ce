import sqlite3
from datetime import datetime

from utilities.db_connection import connect_db

@connect_db
def add_log(conn, cursor, description):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        query = "INSERT INTO logs (timestamp, description) VALUES (?, ?)"
        cursor.execute(query, (timestamp, description))
        conn.commit()
    except Exception as e:
        print("ERROR", str(e))


@connect_db
def get_logs(conn, cursor, limit=50):
    query = "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?"
    cursor.execute(query, (limit,))
    logs = cursor.fetchall()

    logs_list = []

    for log in logs:
        logs_list.append(dict(log))

    return logs_list
