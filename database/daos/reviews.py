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
def get_review_by_participant_id_and_tour_id(conn, cursor, participant_id, tour_id):

    query="SELECT * FROM reviews WHERE participant_id=(?) AND tour_id=(?)"
    cursor.execute(query, (participant_id, tour_id))
    review=cursor.fetchone()

    if review is not None:
        review_obj=Review(review["id"], review["tour_id"], review["participant_id"], review["rating"], review["description"])
        return review_obj
    else:
        return None

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
