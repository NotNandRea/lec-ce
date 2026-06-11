import sqlite3

from utilities.db_connection import connect_db


@connect_db
def get_languages(conn, cursor):
    query="SELECT * FROM languages"
    cursor.execute(query)
    languages=cursor.fetchall()

    languages_list=[]

    for language in languages:
        languages_list.append(dict(language))

    return languages_list

@connect_db
def count_languages(conn, cursor):
    query="SELECT COUNT(*) AS count FROM languages"
    cursor.execute(query)
    count=cursor.fetchone()["count"]

    return count

@connect_db
def add_language_to_user(conn, cursor, user, languages):

    for language in languages:
        query="INSERT INTO guide_speaks (guide_id, language_id) VALUES (?, ?)"
        cursor.execute(query, (user.id, language["id"]))
    
    conn.commit()

@connect_db
def get_languages_by_user_id(conn, cursor, user_id):
    query="SELECT name FROM languages, guide_speaks WHERE languages.id = guide_speaks.language_id AND guide_speaks.guide_id = ?"
    cursor.execute(query, (user_id,))
    languages=cursor.fetchall()

    languages_list=[]

    for language in languages:
        languages_list.append(dict(language))

    return languages_list