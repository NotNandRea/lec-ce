import sqlite3

from database.models.tour import Tour

from utilities.db_connection import connect_db

#CORE FUNCTIONS

@connect_db
def get_tours(conn, cursor):

    query="SELECT * FROM tours"
    cursor.execute(query)
    tours=cursor.fetchall()

    tours_list=[]

    for tour in tours:
        tour_obj=Tour(tour["id"], tour["guide_id"], tour["language_id"], tour["theme_id"], tour["title"], tour["description"], tour["meeting_point"], tour["duration"], tour["max_people"])
        tours_list.append(tour_obj)

    return tours_list

@connect_db
def get_tour_by_id(conn, cursor, id):

    query="SELECT * FROM tours WHERE id=(?)"
    cursor.execute(query, (id,))
    tour=cursor.fetchone()

    if tour is None:
        return None
    tour_obj=Tour(tour["id"], tour["guide_id"], tour["language_id"], tour["theme_id"], tour["title"], tour["description"], tour["meeting_point"], tour["duration"], tour["max_people"])

    return tour_obj

@connect_db
def get_tours_by_guide_id(conn, cursor, guide_id):

    query="SELECT * FROM tours WHERE guide_id=(?)"
    cursor.execute(query, (guide_id,))
    tours=cursor.fetchall()

    tours_list=[]

    for tour in tours:
        tour_obj=Tour(tour["id"], tour["guide_id"], tour["language_id"], tour["theme_id"], tour["title"], tour["description"], tour["meeting_point"], tour["duration"], tour["max_people"])
        tours_list.append(tour_obj)

    return tours_list

@connect_db
def add_tour(conn, cursor, tour):

    success = False
    query = "INSERT INTO tours (id, guide_id, language_id, theme_id, title, description, meeting_point, duration, max_people) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

    try:
        cursor.execute(query, (tour.id, tour.guide_id, tour.language_id, tour.theme_id, tour.title, tour.description, tour.meeting_point, tour.duration, tour.max_people))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def update_tour(conn, cursor, tour):
    
    success = False
    query = "UPDATE tours SET guide_id=(?), language_id=(?), theme_id=(?), title=(?), description=(?), meeting_point=(?), duration=(?), max_people=(?) WHERE id=(?)"

    try:
        cursor.execute(query, (tour.guide_id, tour.language_id, tour.theme_id, tour.title, tour.description, tour.meeting_point, tour.duration, tour.max_people, tour.id))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def delete_tour(conn, cursor, tour):
    
    success = False
    query = "DELETE FROM tours WHERE id=(?)"

    try:
        cursor.execute(query, (tour.id,))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

#UTILITY FUNCTIONS

@connect_db
def count_tours(conn, cursor):
    
    query="SELECT COUNT(*) AS count FROM tours"
    cursor.execute(query)
    count=cursor.fetchone()["count"]

    return count

@connect_db
def get_random_tour(conn, cursor):

    query="SELECT * FROM tours ORDER BY RANDOM() LIMIT 1"
    cursor.execute(query)
    tour=cursor.fetchone()

    if tour is None:
        return None
    tour_obj=Tour(tour["id"], tour["guide_id"], tour["language_id"], tour["theme_id"], tour["title"], tour["description"], tour["meeting_point"], tour["duration"], tour["max_people"])

    return tour_obj