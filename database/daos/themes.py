import sqlite3

from database.models.theme import Theme

from utilities.db_connection import connect_db

@connect_db
def get_themes(conn, cursor):
    query="SELECT * FROM tour_themes"
    cursor.execute(query)
    themes=cursor.fetchall()

    themes_list=[]

    for theme in themes:
        theme_obj=Theme(theme["id"], theme["name"], theme["emoji"], theme["description"])
        themes_list.append(theme_obj)

    return themes_list

@connect_db
def get_theme_by_id(conn, cursor, id):
    query="SELECT * FROM tour_themes WHERE id=(?)"
    cursor.execute(query, (id,))
    theme=cursor.fetchone()

    if theme is None:
        return None
    theme_obj=Theme(theme["id"], theme["name"], theme["emoji"], theme["description"])

    return theme_obj

@connect_db
def get_theme_by_name(conn, cursor, name):
    query="SELECT * FROM tour_themes WHERE name=?"
    cursor.execute(query, (name,))
    theme=cursor.fetchone()

    if theme:
        return Theme(theme["id"], theme["name"], theme["emoji"], theme["description"])
    else:
        return None

@connect_db
def count_themes(conn, cursor):
    query="SELECT COUNT(*) AS count FROM tour_themes"
    cursor.execute(query)
    count=cursor.fetchone()["count"]

    return count