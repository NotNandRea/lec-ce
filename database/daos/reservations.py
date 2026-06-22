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
def get_active_reservation_by_participant_and_occurrence(conn, cursor, participant, occurrence):

    query="SELECT * FROM reservations WHERE participant_id=(?) AND occurrence_id=(?) AND state='active'"
    cursor.execute(query, (participant.id, occurrence.id))
    reservation=cursor.fetchone()

    if reservation is None:
        return None
    reservation_obj=Reservation(reservation["id"], reservation["participant_id"], reservation["occurrence_id"], reservation["timestamp_booking"], reservation["state"])

    return reservation_obj

@connect_db
def get_reservations_by_participant_id(conn, cursor, participant_id, limit=None, after_date=None, reverse_order=False):

    #here we need to join in order to order by date that is in occurrencies table
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
def get_active_reservations_by_participant_id(conn, cursor, participant_id):

    query="SELECT * FROM reservations WHERE participant_id=(?) AND state='active'"
    cursor.execute(query, (participant_id,))
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

@connect_db
def get_active_reservations_by_occurrence_id(conn, cursor, occurrence_id):

    query="SELECT * FROM reservations WHERE occurrence_id=(?) AND state='active'"
    cursor.execute(query, (occurrence_id,))
    reservations=cursor.fetchall()

    reservation_list=[]
    for reservation in reservations:
        reservation_list.append(Reservation(reservation["id"], reservation["participant_id"], reservation["occurrence_id"], reservation["timestamp_booking"], reservation["state"]))

    return reservation_list

@connect_db
def count_active_passed_reservations_by_participant_id_and_tour_id(conn, cursor, participant_id, tour_id, today_date):

    query="SELECT COUNT(*) as count FROM reservations, tour_occurrences WHERE reservations.occurrence_id = tour_occurrences.id AND reservations.participant_id=(?) AND tour_occurrences.tour_id=(?) AND reservations.state='active' AND tour_occurrences.date < (?)"
    cursor.execute(query, (participant_id, tour_id, today_date.strftime("%Y-%m-%d")))
    count=cursor.fetchone()["count"]

    return count

@connect_db
def count_reservations_by_tour_id(conn, cursor, tour_id, state=None, after_date=None):

    query="SELECT COUNT(*) as count FROM reservations, tour_occurrences WHERE reservations.occurrence_id = tour_occurrences.id AND tour_occurrences.tour_id=(?)"
    parameters = (tour_id,)

    if state is not None:
        query += " AND reservations.state=(?)"
        parameters += (state,)
    if after_date is not None:
        query += " AND tour_occurrences.date >= (?)"
        parameters += (after_date.strftime("%Y-%m-%d"),)

    cursor.execute(query, parameters)
    count=cursor.fetchone()["count"]

    return count

@connect_db
def update_reservation_state(conn, cursor, reservation_id, new_state):

    success=False
    query="UPDATE reservations SET state=(?) WHERE id=(?)"
    
    try:
        cursor.execute(query, (new_state, reservation_id))
        conn.commit()
        success=True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def count_reservations(conn, cursor, state=None):

    query="SELECT COUNT(*) as count FROM reservations"
    parameters = ()

    if state is not None:
        query += " WHERE state=(?)"
        parameters += (state,)

    cursor.execute(query, parameters)
    count=cursor.fetchone()["count"]

    return count

@connect_db
def count_reservations_by_language_id(conn, cursor, language_id, state=None):

    query="SELECT COUNT(*) as count FROM reservations, tour_occurrences, tours WHERE reservations.occurrence_id = tour_occurrences.id AND tour_occurrences.tour_id=tours.id AND tours.language_id=(?)"
    parameters = (language_id,)

    if state is not None:
        query += " AND reservations.state=(?)"
        parameters += (state,)

    cursor.execute(query, parameters)
    count=cursor.fetchone()["count"]

    return count

@connect_db
def count_reservations_by_theme_id(conn, cursor, theme_id, state=None):

    query="SELECT COUNT(*) as count FROM reservations, tour_occurrences, tours WHERE reservations.occurrence_id = tour_occurrences.id AND tour_occurrences.tour_id=tours.id AND tours.theme_id=(?)"
    parameters = (theme_id,)

    if state is not None:
        query += " AND reservations.state=(?)"
        parameters += (state,)

    cursor.execute(query, parameters)
    count=cursor.fetchone()["count"]

    return count