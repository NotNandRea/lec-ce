import sqlite3

from utilities.db_connection import connect_db

@connect_db
def get_admin_by_username(conn, cursor, username):
    query="SELECT * FROM admins WHERE username=(?)"
    cursor.execute(query, (username,))
    admin=cursor.fetchone()

    if admin is None:
        return None

    admin_dict = { "id": admin["id"], "username": admin["username"], "password": admin["password"], "first_name": admin["first_name"], "last_name": admin["last_name"] }
    return admin_dict