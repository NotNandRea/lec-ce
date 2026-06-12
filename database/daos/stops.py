import sqlite3

from database.models.tour import Tour

from utilities.db_connection import connect_db

@connect_db
def add_stops_to_tour(conn, cursor, tour, stops):

    success = False
    query = "INSERT INTO stops (tour_id, place_name, order_number) VALUES (?, ?, ?)"

    try:
        order_number = 1

        for stop in stops:
            cursor.execute(query, (tour.id, stop, order_number))
            order_number=order_number + 1
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR:", str(e))
        conn.rollback()
        success = False

    return success

@connect_db
def get_stops_by_tour(conn, cursor, tour):

    query = "SELECT order_number, place_name FROM stops WHERE tour_id=(?) ORDER BY order_number ASC"
    cursor.execute(query, (tour.id,))
    stops = cursor.fetchall()

    stops_dict = {}

    for stop in stops:
        stops_dict[f"{stop['order_number']}"] = stop["place_name"]

    return stops_dict

@connect_db
def get_first_stop_by_tour(conn, cursor, tour):

    query = "SELECT place_name FROM stops WHERE tour_id=(?) ORDER BY order_number ASC LIMIT 1"
    cursor.execute(query, (tour.id,))
    stop = cursor.fetchone()

    if stop:
        return stop["place_name"]
    else:
        return None