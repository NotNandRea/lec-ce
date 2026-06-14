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
    occurrence_obj=Occurrence(occurrence["id"], occurrence["tour_id"], datetime.datetime.strptime(occurrence["date"], "%Y-%m-%d").date(), occurrence["start_time"], occurrence["state"])

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

@connect_db
def get_occurrence_by_id(conn, cursor, occurrence_id):

    query="SELECT * FROM tour_occurrences WHERE id=(?)"
    cursor.execute(query, (occurrence_id,))
    occurrence=cursor.fetchone()

    if occurrence is None:
        return None
    occurrence_obj=Occurrence(occurrence["id"], occurrence["tour_id"], datetime.datetime.strptime(occurrence["date"], "%Y-%m-%d").date(), occurrence["start_time"], occurrence["state"])

    return occurrence_obj

#not empty means that there is at least one reservation that is not canceled
@connect_db
def get_not_empty_occurrences_by_guide_id(conn, cursor, guide_id, limit=None, after_date=None, reverse_order=False):

    query="SELECT DISTINCT tour_occurrences.* FROM tour_occurrences, reservations, tours WHERE tour_occurrences.id = reservations.occurrence_id AND tour_occurrences.tour_id = tours.id AND tours.guide_id = ? AND reservations.state != 'canceled'"
    parameters = (guide_id,)

    if after_date is not None:
       query += " AND tour_occurrences.date >= ?"
       parameters += (after_date.strftime("%Y-%m-%d"),)
    
    if reverse_order:
        query += "  ORDER BY tour_occurrences.date DESC"
    else:
        query += "  ORDER BY tour_occurrences.date ASC"

    if limit is not None:
        query += " LIMIT ?"
        parameters += (limit,)

    
    cursor.execute(query, parameters)
    occurrences=cursor.fetchall()

    occurrence_list=[]
    for occurrence in occurrences:
        occurrence_list.append(Occurrence(occurrence["id"], occurrence["tour_id"], datetime.datetime.strptime(occurrence["date"], "%Y-%m-%d").date(), occurrence["start_time"], occurrence["state"]))

    return occurrence_list

#TODO: when editing a tour but a reservation was made and canceled, delete the occurrence