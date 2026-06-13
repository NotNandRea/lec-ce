import sqlite3

from database.models.reservation import Reservation

from utilities.db_connection import connect_db

@connect_db
def add_reservation(conn, cursor, reservation):

    success=False
    query="INSERT INTO reservations (id, participant_id, occurrence_id, timestamp_booking) VALUES (?, ?, ?, ?)"
    
    try:
        cursor.execute(query, (reservation.id, reservation.participant_id, reservation.occurrence_id, reservation.timestamp_booking))
        conn.commit()
        success=True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def get_reservation_by_participant_and_occurrence(conn, cursor, participant, occurrence):

    query="SELECT * FROM reservations WHERE participant_id=(?) AND occurrence_id=(?)"
    cursor.execute(query, (participant.id, occurrence.id))
    reservation=cursor.fetchone()

    if reservation is None:
        return None
    reservation_obj=Reservation(reservation["id"], reservation["participant_id"], reservation["occurrence_id"], reservation["timestamp_booking"], reservation["state"])

    return reservation_obj

@connect_db
def get_reservations_by_participant_id(conn, cursor, participant_id, limit=None, after_date=None, reverse_order=False):

    query="SELECT * FROM reservations, tour_occurrences, tours WHERE reservations.occurrence_id=tour_occurrences.id AND tour_occurrences.tour_id=tours.id AND reservations.participant_id=(?)"
    parameters=(participant_id,)

    
    if after_date is not None:
        query += " AND tour_occurrences.date >= ?"
        parameters += (after_date.strftime("%Y-%m-%d"),)

    if reverse_order:
        query += " ORDER BY tour_occurrences.date DESC"
    else:
        query += " ORDER BY tour_occurrences.date ASC"

    if limit is not None:
        query += " LIMIT ?"
        parameters += (limit,)

    cursor.execute(query, parameters)
    reservations=cursor.fetchall()

    reservation_list=[]
    for reservation in reservations:
        reservation_list.append(Reservation(reservation["id"], reservation["participant_id"], reservation["occurrence_id"], reservation["timestamp_booking"], reservation["state"]))

    return reservation_list

@connect_db
def get_reservation_by_id(conn, cursor, reservation_id):

    query="SELECT * FROM reservations WHERE id=(?)"
    cursor.execute(query, (reservation_id,))
    reservation=cursor.fetchone()

    if reservation is None:
        return None
    reservation_obj=Reservation(reservation["id"], reservation["participant_id"], reservation["occurrence_id"], reservation["timestamp_booking"], reservation["state"])

    return reservation_obj