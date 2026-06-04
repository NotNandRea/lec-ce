import sqlite3

from database.models.review import Review

from utilities.db_connection import connect_db

@connect_db
def get_reviews_by_tour_id(conn, cursor, tour_id):

    query="SELECT * FROM reviews WHERE tour_id=(?)"
    cursor.execute(query, (tour_id,))
    reviews=cursor.fetchall()

    reviews_list=[]

    for review in reviews:
        review_obj=Review(review["id"], review["tour_id"], review["participant_id"], review["rating"], review["description"])
        reviews_list.append(review_obj)

    return reviews_list

@connect_db
def add_review(conn, cursor, review):

    success = False
    query = "INSERT INTO reviews (id, tour_id, participant_id, rating, description) VALUES (?, ?, ?, ?, ?)"

    try:
        cursor.execute(query, (review.id, review.tour_id, review.participant_id, review.rating, review.description))
        conn.commit()
        success = True
    except Exception as e:
        print("ERROR", str(e))
        conn.rollback()

    return success

@connect_db
def count_reviews_of_a_tour(conn, cursor, tour_id):

    query="SELECT COUNT(*) AS count FROM reviews WHERE tour_id=(?)"
    cursor.execute(query, (tour_id,))
    count=cursor.fetchone()["count"]

    return count

@connect_db
def average_rating_of_a_tour(conn, cursor, tour_id):
    
    query="SELECT AVG(rating) AS average FROM reviews WHERE tour_id=(?)"
    cursor.execute(query, (tour_id,))
    average=cursor.fetchone()["average"]

    return average