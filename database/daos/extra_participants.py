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