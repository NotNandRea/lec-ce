import sqlite3
import uuid

from database.models.tour import Tour

from utilities.db_connection import connect_db

@connect_db
def add_photos_to_tour(conn, cursor, tour, photos):

    success = False
    query = "INSERT INTO tour_photos (tour_id, path, order_number) VALUES (?, ?, ?)"

    try:
        for i in range(1, 6):
            cursor.execute(query, (tour.id, photos.get(str(i)), i))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR:", str(e))
        conn.rollback()
    return success

@connect_db
def update_photo_to_tour(conn, cursor, tour, photo_number, new_photo_path):

    success = False
    query = "UPDATE tour_photos SET path=(?) WHERE tour_id=(?) AND order_number=(?)"

    try:
        cursor.execute(query, (new_photo_path, tour.id, photo_number))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR:", str(e))
        conn.rollback()
    return success

@connect_db
def get_tour_photos(conn, cursor, tour):
    query="SELECT order_number, path FROM tour_photos WHERE tour_id=(?) ORDER BY order_number"
    cursor.execute(query, (tour.id,))
    photos=cursor.fetchall()

    photos_dict={}

    for photo in photos:
        photos_dict[f"photo{photo['order_number']}"] = photo["path"]

    return photos_dict

@connect_db
def get_first_photo(conn, cursor, tour):
    query="SELECT path FROM tour_photos WHERE tour_id=(?) ORDER BY order_number LIMIT 1"
    cursor.execute(query, (tour.id,))
    photo=cursor.fetchone()

    if photo:
        return photo["path"]
    else:
        return None