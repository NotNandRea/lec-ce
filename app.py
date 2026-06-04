import os
from dotenv import load_dotenv

from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from database.models.user import User
from database.daos import users as users_dao
from database.daos import tours as tours_dao
from database.daos import utilities as utilities_dao

from utilities import check_email, check_password, images, role_routes

import uuid
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename



#load everythings from .env file
load_dotenv()

app=Flask(__name__)
app.config["SECRET_KEY"]=os.getenv("APP-SECRET-KEY")  #loads the key from .env

login_manager= LoginManager()
login_manager.init_app(app)


# AUTH BUISNESS LOGIC

@login_manager.user_loader
def load_user(user_id):
    db_user=users_dao.get_user_by_id(user_id)

    return db_user

@app.route("/register", methods=["POST"])
def register_post():

    user=request.form.to_dict()

    # role validation
    role = user.get("role")
    if role in [None, ""]:
        return "Invalid role", 400
    if role not in ["participant","guide"]:
        return "Invalid role", 400
    
    #email validation
    email= user.get("email")
    if email in [None, ""]:
        return "Invalid email", 400
    if check_email.check_email(email) == False:
        return "Invalid email", 400
    if users_dao.get_user_by_email(email):
        return "User already registered", 400
    
    # password validation
    password= user.get("password")
    if password in [None, ""]:
        return "Invalid password", 400
    if check_password.check_password(password) == False:
        return "Invalid password", 400
    password=generate_password_hash(password)

    #name validation
    first_name= user.get("first_name")
    if first_name in [None, ""]:
        return "Invalid first name", 400
    
    # name validation
    last_name= user.get("last_name")
    if last_name in [None, ""]:
        return "Invalid last name", 400
    
    #image validartion
    profile_photo= request.files.get("profile_photo", None)
    profile_photo_filename = None
    if profile_photo:

        #file type verification
        if not images.is_image(profile_photo):
            return "Not an image or image too small", 400

        #image resizing
        profile_photo= images.to_square(profile_photo)

        #file naming
        extension=profile_photo.filename.split(".")[-1].lower()
        profile_photo_filename=str(uuid.uuid4()) + "." + extension
        profile_photo.save("profile_photos/" + profile_photo_filename)
    else:
        profile_photo_filename="profile_photos/default.png"
    
    id=str(uuid.uuid4())

    user_obj=User(id, role, email, password, first_name, last_name, profile_photo_filename)

    users_dao.add_user(user_obj)

    return "ok", 200

@app.route("/login", methods=["POST"])
def login():
    
    user=request.form.to_dict()

    # email validation
    email= user.get("email")
    if email in [None, ""]:
        return "Invalid email", 400
    if check_email.check_email(email) == False:
        return "Invalid email", 400
    
    user_obj=users_dao.get_user_by_email(email)

    if user_obj is None:
        return "Authentication Error", 400
    
    # password validation
    password= user.get("password")
    if password in [None, ""]:
        return "Invalid password", 400

    if not user_obj.check_password(password):
        return "Authentication Error", 400

    login_user(user_obj)

    return "ok", 200

@app.route("/logout")
@login_required
def logout():
    logout_user()

    return "ok", 200

# NOT LOGIN PROTECTED ROUTES

@app.route("/")
def home():

    tours=tours_dao.get_tours()
    tomorrow_tour=tours_dao.get_tomorrow_tour()
    
    tour_numnber=tours_dao.count_tours()
    guides_number=users_dao.count_guides()
    participants_number=users_dao.count_participants()
    languages_number=utilities_dao.count_languages()
    themes_number=utilities_dao.count_themes()

    return render_template("home.html", tours=tours, tour_number=tour_numnber, guides_number=guides_number, participants_number=participants_number, tomorrow_tour=tomorrow_tour, languages_number=languages_number, themes_number=themes_number)


