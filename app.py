import os
from dotenv import load_dotenv

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from database.models.user import User
from database.models.tour import Tour
from database.models.theme import Theme

from database.daos import users as users_dao
from database.daos import tours as tours_dao
from database.daos import themes as themes_dao
from database.daos import languages as languages_dao

from utilities import check_email, check_password, images
from utilities.role_decorators import guide_required
from utilities.days_to_numbers import days_to_numbers

import uuid
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from datetime import date

# TODO: REMOVE THIS PLACEHOLDER FOR TESTING
placeholder_guide=User("guide-id", "guide", "", "", "John", "Doe", profile_photo=None)
placeholder_guide.languages = ["English", "Italian"]

placeholder_theme = Theme("Baroque", "⛪")

placeholder_tour=Tour(id, "Barocco", "Tour Description", 120, 11)
placeholder_tour.photos = {"photo1": "placeholder2.jpg", "photo2": "placeholder.jpg", "photo3": "placeholder2.jpg", "photo4": "placeholder.jpg", "photo5": "placeholder2.jpg"}
placeholder_tour.theme = placeholder_theme
placeholder_tour.guide = placeholder_guide
placeholder_tour.language = "English"
placeholder_tour.weekly_schedule = {"monday": None, "tuesday": "10:00", "wednesday": "14:00", "thursday": "16:00", "friday": None, "saturday": "12:00", "sunday": None}
placeholder_tour.stops = ["Stop 1", "Stop 2", "Stop 3", "Stop 4"]


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

    if current_user.is_authenticated:
        flash("You are already logged in", "negative")
        return redirect(url_for("home"))

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


        extension=secure_filename(profile_photo.filename).split(".")[-1].lower()
        profile_photo_filename=str(uuid.uuid4()) + "." + extension

        #image resizing
        profile_photo= images.to_square(profile_photo)

        #file naming
        profile_photo.save("static/images/profile_photos/" + profile_photo_filename)
    else:
        profile_photo_filename=None
    
    id=str(uuid.uuid4())


    #languages validation
    if role == "guide":
        selected_languages = request.form.getlist("languages")
        available_languages = languages_dao.get_languages()

        available_names = []

        for language in available_languages:
            available_names.append(language["name"])

        invalid_languages = []

        for language in selected_languages:
            if language not in available_names:
                invalid_languages.append(language)

        if len(invalid_languages) > 0:
            return "Invalid languages", 400
        
        guide_languages = []

        for language in available_languages:
            if language["name"] in selected_languages:
                guide_languages.append(language)
        
        if len(selected_languages) == 0:
            return "At least one language must be selected for guides", 400
    else:
        guide_languages = None

    user_obj=User(id, role, email, password, first_name, last_name, profile_photo_filename)

    users_dao.add_user(user_obj)

    if guide_languages is not None:
        languages_dao.add_language_to_user(user_obj, guide_languages)

    login_user(user_obj)

    return redirect(url_for("home"))

@app.route("/login", methods=["POST"])
def login_post():

    if current_user.is_authenticated:
        flash("You are already logged in", "negative")
        return redirect(url_for("home"))
    
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

    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for("home"))


@app.route("/register")
def register():
    if current_user.is_authenticated:
        flash("You are already logged in", "negative")
        return redirect(url_for("home"))

    languages=languages_dao.get_languages()

    return render_template("register.html", languages=languages)

@app.route("/login")
def login():

    if current_user.is_authenticated:
        flash("You are already logged in", "negative")
        return redirect(url_for("home"))

    return render_template("login.html")


# NON-AUTH ROUTES

@login_required
@app.route("/me")
def my_profile():
    return render_template("profile.html")

@app.route("/")
def home():

    today=date.today()
    languages=languages_dao.get_languages()
    themes=themes_dao.get_themes()

    return render_template("home.html", today=today, languages=languages, themes=themes, tours=[placeholder_tour])

@app.route("/tours/new")
@login_required
@guide_required
def new_tour():

    languages=languages_dao.get_languages()
    themes=themes_dao.get_themes()

    return render_template("new_tour.html", languages=languages, themes=themes, origin="new")

#TODO: remove placeholder
@app.route("/tours/edit/<id>")
@login_required
@guide_required
def edit_tour(id):

    languages=languages_dao.get_languages()
    themes=themes_dao.get_themes()

    return render_template("new_tour.html", languages=languages, themes=themes, origin="edit", tour=placeholder_tour)

#TODO: remove placeholder
@app.route("/tours/list")
def tours():

    languages=languages_dao.get_languages()
    themes=themes_dao.get_themes()


    return render_template("tours.html", languages=languages, themes=themes, tours=[placeholder_tour])

#TODO: fix avaiable users issue, which date referring?
@app.route("/tour/<id>")
def tour(id):

    theme=placeholder_tour.theme.name.lower()
    avaiable_days=days_to_numbers(placeholder_tour)

    return render_template("tour.html", tour=placeholder_tour, theme=theme, avaiable_days=avaiable_days)
