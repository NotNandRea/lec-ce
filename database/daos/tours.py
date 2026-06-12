import sqlite3

from database.models.tour import Tour

from utilities.db_connection import connect_db

#CORE FUNCTIONS

@connect_db
def get_tours(conn, cursor, limit=None):

    query="SELECT * FROM tours"
    if limit is not None:
        query += " LIMIT (?)"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)
    tours=cursor.fetchall()

    tours_list=[]

    for tour in tours:
        tour_obj=Tour(tour["id"], tour["title"], tour["description"], tour["duration"], tour["max_participants"], tour["theme_id"], tour["language_id"], tour["guide_id"])
        tours_list.append(tour_obj)

    return tours_list

@connect_db
def get_tour_by_id(conn, cursor, id):

    query="SELECT * FROM tours WHERE id=(?)"
    cursor.execute(query, (id,))
    tour=cursor.fetchone()

    if tour is None:
        return None
    tour_obj=Tour(tour["id"], tour["title"], tour["description"], tour["duration"], tour["max_participants"], tour["theme_id"], tour["language_id"], tour["guide_id"])

    return tour_obj

@connect_db
def get_tours_by_guide_id(conn, cursor, guide_id):

    query="SELECT * FROM tours WHERE guide_id=(?)"
    cursor.execute(query, (guide_id,))
    tours=cursor.fetchall()

    tours_list=[]

    for tour in tours:
        tour_obj=Tour(tour["id"], tour["title"], tour["description"], tour["duration"], tour["max_participants"], tour["theme_id"], tour["language_id"], tour["guide_id"])
        tours_list.append(tour_obj)

    return tours_list

@connect_db
def add_tour(conn, cursor, tour):

    success = False
    query = "INSERT INTO tours (id, title, description, duration, max_participants, language_id, guide_id, theme_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    try:
        cursor.execute(query, (tour.id, tour.title, tour.description, tour.duration, tour.max_participants, tour.language["id"], tour.guide.id, tour.theme.id))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def add_schedule_to_tour(conn, cursor, tour, schedule):

    success = False
    query = "INSERT INTO tour_week_slots (tour_id, day, time) VALUES (?, ?, ?)"

    try:
        for day, time in schedule.items():
            if time is not None:
                cursor.execute(query, (tour.id, day, time))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def get_schedule_by_tour(conn, cursor, tour):

    query = "SELECT day, time FROM tour_week_slots WHERE tour_id=(?)"
    cursor.execute(query, (tour.id,))
    schedule = cursor.fetchall()

    schedule_dict = {"monday": None, "tuesday": None, "wednesday": None, "thursday": None, "friday": None, "saturday": None, "sunday": None}
    for slot in schedule:
        schedule_dict[slot["day"]] = slot["time"]

    return schedule_dict

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