import sqlite3
from database.models.user import User

def get_users():
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query="SELECT * FROM users"
    cursor.execute(query)
    users=cursor.fetchall()

    cursor.close()
    conn.close()

    users_list=[]

    for user in users:
        user_obj=User(user["id"], user["role"], user["email"], user["password"], user["first_name"], user["last_name"], user["profile_photo"])
        users_list.append(user_obj)

    return users_list


def get_user_by_id(id):
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query="SELECT * FROM users WHERE id=(?)"
    cursor.execute(query, (id,))
    user=cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return None
    user_obj=User(user["id"], user["role"], user["email"], user["password"], user["first_name"], user["last_name"], user["profile_photo"])

    return user_obj

def get_user_by_email(email):
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query="SELECT * FROM users WHERE email=(?)"
    cursor.execute(query, (email,))
    user=cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return None
    user_obj=User(user["id"], user["role"], user["email"], user["password"], user["first_name"], user["last_name"], user["profile_photo"])

    return user_obj

def add_user(user):
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    query = "INSERT INTO users (id, role, email, password, first_name, last_name, profile_photo) VALUES (?, ?, ?, ?, ?, ?, ?)"

    try:
        cursor.execute(query, (user.id, user.role, user.email, user.password, user.first_name, user.last_name, user.profile_photo))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()
    
    cursor.close()
    conn.close()

    return success