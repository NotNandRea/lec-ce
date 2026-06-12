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
