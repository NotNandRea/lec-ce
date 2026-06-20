import sqlite3

from database.models.report import Report

from utilities.db_connection import connect_db

@connect_db
def add_report(conn, cursor, report):

    success=False
    query="INSERT INTO post_reports (id, occurrence_id, actual_participants, photo) VALUES (?, ?, ?, ?)"

    try:
        cursor.execute(query, (report.id, report.occurrence_id, report.actual_participants, report.photo_path))
        conn.commit()
        success=True
    except Exception as e:
        print("Error", str(e))
        conn.rollback()
    return success

@connect_db
def get_report_by_occurrence_id(conn, cursor, occurrence_id):

    query="SELECT * FROM post_reports WHERE occurrence_id=(?)"
    cursor.execute(query, (occurrence_id,))
    result=cursor.fetchone()

    if result is None:
        return None

    report = Report(result["id"], result["occurrence_id"], result["actual_participants"], result["photo"])
    
    return report