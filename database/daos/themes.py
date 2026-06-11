import sqlite3

from utilities.db_connection import connect_db

@connect_db
def get_themes(conn, cursor):
    query="SELECT * FROM tour_themes"
    cursor.execute(query)
    themes=cursor.fetchall()

    themes_list=[]

    for theme in themes:
        themes_list.append(dict(theme))

    return themes_list

@connect_db
def count_themes(conn, cursor):
    query="SELECT COUNT(*) AS count FROM tour_themes"
    cursor.execute(query)
    count=cursor.fetchone()["count"]

    return count