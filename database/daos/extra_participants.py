import sqlite3

from database.models.extra_participant import Extra_Participant

from utilities.db_connection import connect_db

@connect_db
def add_extra_participant(conn, cursor, extra_participant):

    success=False
    query="INSERT INTO extra_participants (id, first_name, last_name, email, reservation_id) VALUES (?, ?, ?, ?, ?)"
    
    try:
        cursor.execute(query, (extra_participant.id, extra_participant.first_name, extra_participant.last_name, extra_participant.email, extra_participant.reservation_id))
        conn.commit()
        success=True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def get_extra_participants_by_reservation_id(conn, cursor, reservation_id):

    query="SELECT * FROM extra_participants WHERE reservation_id=(?)"
    cursor.execute(query, (reservation_id,))
    extra_participants=cursor.fetchall()

    extra_participant_list=[]
    for extra_participant in extra_participants:
        extra_participant_list.append(Extra_Participant(extra_participant["id"], extra_participant["first_name"], extra_participant["last_name"], extra_participant["email"]))

    return extra_participant_list