import datetime
import sqlite3

from database.models.occurrence import Occurrence

from utilities.db_connection import connect_db

@connect_db
def get_occurrence_by_tour_and_date(conn, cursor, tour_id, date):

    query="SELECT * FROM tour_occurrences WHERE tour_id=(?) AND date=(?)"
    cursor.execute(query, (tour_id, date.strftime("%Y-%m-%d")))
    occurrence=cursor.fetchone()

    if occurrence is None:
        return None
    occurrence_obj=Occurrence(occurrence["id"], occurrence["tour_id"], datetime.datetime.strptime(occurrence["date"], "%Y-%m-%d"), occurrence["start_time"], occurrence["state"])

    return occurrence_obj

@connect_db
def add_occurrence(conn, cursor, occurrence):

    success=False
    query="INSERT INTO tour_occurrences (id, tour_id, date, start_time) VALUES (?, ?, ?, ?)"
    
    try:
        cursor.execute(query, (occurrence.id, occurrence.tour_id, occurrence.date.strftime("%Y-%m-%d"), occurrence.start_time))
        conn.commit()
        success=True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def get_participants_number(conn, cursor, occurrence):

    query="SELECT COUNT(*) as num_participants FROM reservations WHERE occurrence_id=(?)"
    cursor.execute(query, (occurrence.id,))
    num_participants=cursor.fetchone()

    return int(num_participants["num_participants"])