import sqlite3

from database.models.tour import Tour

from utilities.db_connection import connect_db

#CORE FUNCTIONS

@connect_db
def get_tours_filters(conn, cursor, limit=None, state=None, weekday=None, duration_start=None, duration_end=None, language=None, theme=None, max_participants=None, min_participants=None):

    query="SELECT DISTINCT tours.* FROM tours, tour_week_slots WHERE tours.id = tour_week_slots.tour_id"
    parameters = ()

    if state is not None:
        query += " AND state=(?)"
        parameters += (state,)

    if weekday is not None:
        query += " AND tour_week_slots.day IN ("
        for i in range(len(weekday)):
            query += "?"
            if i < len(weekday) - 1:
                query += ", "
        query += ")"
        parameters += tuple(weekday)

    if duration_start is not None:
        query += " AND duration >= (?)"
        parameters += (duration_start,)

    if duration_end is not None:
        query += " AND duration <= (?)"
        parameters += (duration_end,)

    if language is not None:
        query += " AND language_id=(?)"
        parameters += (language,)

    if theme is not None:
        query += " AND theme_id=(?)"
        parameters += (theme,)

    if max_participants is not None:
        query += " AND max_participants<=(?)"
        parameters += (max_participants,)

    if min_participants is not None:
        query += " AND max_participants>=(?)"
        parameters += (min_participants,)

    if limit is not None:
        query += " LIMIT (?)"
        parameters += (limit,)

    cursor.execute(query, parameters)
    tours=cursor.fetchall()

    tours_list=[]

    for tour in tours:
        tour_obj=Tour(tour["id"], tour["title"], tour["description"], tour["duration"], tour["max_participants"], tour["theme_id"], tour["language_id"], tour["guide_id"], tour["state"])
        tours_list.append(tour_obj)

    return tours_list


@connect_db
def get_tour_by_id(conn, cursor, id):

    query="SELECT * FROM tours WHERE id=(?)"
    cursor.execute(query, (id,))
    tour=cursor.fetchone()

    if tour is None:
        return None
    tour_obj=Tour(tour["id"], tour["title"], tour["description"], tour["duration"], tour["max_participants"], tour["theme_id"], tour["language_id"], tour["guide_id"], tour["state"])

    return tour_obj

@connect_db
def get_tours_by_guide_id(conn, cursor, guide_id, limit=None, state=None):

    query="SELECT * FROM tours WHERE guide_id=(?)"
    parameters = (guide_id,)
    if state is not None:
        query += " AND state=(?)"
        parameters += (state,)
    if limit is not None:
        query += " LIMIT (?)"
        parameters += (limit,)
    
    cursor.execute(query, parameters)
    
    tours=cursor.fetchall()

    tours_list=[]

    for tour in tours:
        tour_obj=Tour(tour["id"], tour["title"], tour["description"], tour["duration"], tour["max_participants"], tour["theme_id"], tour["language_id"], tour["guide_id"], tour["state"])
        tours_list.append(tour_obj)

    return tours_list

@connect_db
def get_times_and_duration_of_tours_by_guide_id_and_day(conn, cursor, guide_id, day):

    query="SELECT tour_week_slots.time, tours.duration FROM tours, tour_week_slots WHERE tours.id = tour_week_slots.tour_id AND tours.guide_id=(?) AND tour_week_slots.day=(?) AND tours.state='active'"
    cursor.execute(query, (guide_id, day))
    results=cursor.fetchall()

    temp = []
    for result in results:
        temp.append((result["time"], int(result["duration"])))

    return temp

@connect_db
def get_times_and_duration_of_tours_by_guide_id_and_day_this_excluded(conn, cursor, guide_id, day, tour_id):

    query="SELECT tour_week_slots.time, tours.duration FROM tours, tour_week_slots WHERE tours.id = tour_week_slots.tour_id AND tours.guide_id=(?) AND tour_week_slots.day=(?) AND tours.state='active' AND tours.id != (?)"
    cursor.execute(query, (guide_id, day, tour_id))
    results=cursor.fetchall()

    temp = []
    for result in results:
        temp.append((result["time"], int(result["duration"])))

    return temp

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
def update_tour(conn, cursor, tour):

    success = False
    query = "UPDATE tours SET title=(?), description=(?), duration=(?), max_participants=(?), language_id=(?), theme_id=(?) WHERE id=(?)"

    try:
        cursor.execute(query, (tour.title, tour.description, tour.duration, tour.max_participants, tour.language["id"], tour.theme.id, tour.id))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def update_tour_schedule(conn, cursor, tour, schedule):

    success = False
    delete_query = "DELETE FROM tour_week_slots WHERE tour_id=(?)"
    insert_query = "INSERT INTO tour_week_slots (tour_id, day, time) VALUES (?, ?, ?)"

    try:
        cursor.execute(delete_query, (tour.id,))
        for day, time in schedule.items():
            if time is not None:
                cursor.execute(insert_query, (tour.id, day, time))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success

@connect_db
def update_tour_state(conn, cursor, tour, state):

    success = False
    query = "UPDATE tours SET state=(?) WHERE id=(?)"

    try:
        cursor.execute(query, (state, tour.id))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    return success


@connect_db
def count_tours(conn, cursor, state=None):
    
    query="SELECT COUNT(*) AS count FROM tours"
    parameters=()

    if state is not None:
        query+=" WHERE state=(?)"
        parameters=(state,)

    cursor.execute(query, parameters)
    count=cursor.fetchone()["count"]

    return count

@connect_db
def get_weekly_schedule_by_tour(conn, cursor, tour):

    query = "SELECT day, time FROM tour_week_slots WHERE tour_id=(?)"
    cursor.execute(query, (tour.id,))
    schedule = cursor.fetchall()

    schedule_dict = {"monday": None, "tuesday": None, "wednesday": None, "thursday": None, "friday": None, "saturday": None, "sunday": None}
    for slot in schedule:
        schedule_dict[slot["day"]] = slot["time"]

    return schedule_dict
