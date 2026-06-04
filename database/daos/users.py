import sqlite3

from database.models.user import User

from utilities.db_connection import connect_db

#CORE FUNCTIONS

@connect_db
def get_users(conn, cursor):

    query="SELECT * FROM users"
    cursor.execute(query)
    users=cursor.fetchall()

    users_list=[]

    for user in users:
        user_obj=User(user["id"], user["role"], user["email"], user["password"], user["first_name"], user["last_name"], user["profile_photo"])
        users_list.append(user_obj)

    return users_list

@connect_db
def get_user_by_id(conn, cursor, id):

    query="SELECT * FROM users WHERE id=(?)"
    cursor.execute(query, (id,))
    user=cursor.fetchone()

    if user is None:
        return None
    user_obj=User(user["id"], user["role"], user["email"], user["password"], user["first_name"], user["last_name"], user["profile_photo"])

    return user_obj

@connect_db
def get_user_by_email(conn, cursor, email):


    query="SELECT * FROM users WHERE email=(?)"
    cursor.execute(query, (email,))
    user=cursor.fetchone()


    if user is None:
        return None
    user_obj=User(user["id"], user["role"], user["email"], user["password"], user["first_name"], user["last_name"], user["profile_photo"])

    return user_obj

@connect_db
def add_user(conn, cursor, user):

    success = False
    query = "INSERT INTO users (id, role, email, password, first_name, last_name, profile_photo) VALUES (?, ?, ?, ?, ?, ?, ?)"

    try:
        cursor.execute(query, (user.id, user.role, user.email, user.password, user.first_name, user.last_name, user.profile_photo))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()

    return success

# UTILITY FUNCTIONS

@connect_db
def count_guides(conn, cursor):
    
    query="SELECT COUNT(*) AS count FROM users WHERE role='guide'"
    cursor.execute(query)
    result = cursor.fetchone()
    count = result["count"]

    return count

@connect_db
def count_participants(conn, cursor):
    
    query="SELECT COUNT(*) AS count FROM users WHERE role='participant'"
    cursor.execute(query)
    result = cursor.fetchone()
    count = result["count"]

    return count