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
from database.daos import photos as photos_dao
from database.daos import stops as stops_dao

from utilities import check_email, check_password, images, days_to_numbers, check_time
from utilities.role_decorators import guide_required
from utilities.role_decorators import participant_required

from utilities.constants import PROFILE_IMG_HEIGHT, TOUR_PHOTO_IMG_HEIGHT, TOUR_PHOTO_IMG_WIDTH

import uuid
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from datetime import date



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

    # First name validation
    first_name= user.get("first_name")
    if first_name in [None, ""]:
        return "Invalid first name", 400
    
    # Last name validation
    last_name= user.get("last_name")
    if last_name in [None, ""]:
        return "Invalid last name", 400
    
    #image validartion
    profile_photo= request.files.get("profile_photo", None)
    profile_photo_filename = None
    if profile_photo:

        #file type verification
        if not images.is_image(profile_photo):
            return "Not an image", 400
        if not images.is_squareable(profile_photo):
            return f"Image is too small, not squareable, minimum size is {PROFILE_IMG_HEIGHT}x{PROFILE_IMG_HEIGHT}", 400

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

    if not users_dao.add_user(user_obj):
        return "An error occurred, user not created", 500

    if guide_languages is not None:
        if not languages_dao.add_language_to_user(user_obj, guide_languages):
            return "An error occurred, languages not added", 500

    login_user(user_obj)
    flash("Registration successful", "positive")

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

#TODO: unify in one query with joins
@login_required
@app.route("/me")
def my_profile():

    current_user.languages = languages_dao.get_languages_by_user_id(current_user.id)
    
    if current_user.role == "guide":
        tours = tours_dao.get_tours_by_guide_id(current_user.id,6)
        for tour in tours:
            tour.photos=photos_dao.get_first_photo(tour)
            tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
            tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
            tour.stops=stops_dao.get_first_stop_by_tour(tour)
            tour.guide = users_dao.get_user_by_id(tour.guide_id)
    #TODO: implement bookings
    else:
        tours = None

    return render_template("profile.html", tours=tours)

# TOUR LISTING

#TODO: unify in one query with joins
@app.route("/")
def home():

    today=date.today()
    
    tours=tours_dao.get_tours(8)

    for tour in tours:
        tour.photos=photos_dao.get_first_photo(tour)
        tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
        tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
        tour.stops=stops_dao.get_first_stop_by_tour(tour)
        tour.guide = users_dao.get_user_by_id(tour.guide_id)

    return render_template("home.html", today=today, tours=tours)

#TODO: unify in one query with joins
@app.route("/tours/list")
def tours():

    today=date.today()
    
    tours=tours_dao.get_tours(8)

    for tour in tours:
        tour.photos=photos_dao.get_first_photo(tour)
        tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
        tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
        tour.stops=stops_dao.get_first_stop_by_tour(tour)
        tour.guide = users_dao.get_user_by_id(tour.guide_id)

    return render_template("tours.html", today=today, tours=tours)

@app.route("/tour/<id>")
def tour(id):

    today=date.today()

    tour=tours_dao.get_tour_by_id(id)
    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))

    tour.theme = themes_dao.get_theme_by_id(tour.theme_id)
    tour.language = languages_dao.get_language_by_id(tour.language_id)
    tour.weekly_schedule=tours_dao.get_schedule_by_tour(tour)
    tour.photos=photos_dao.get_tour_photos(tour)
    tour.stops=stops_dao.get_stops_by_tour(tour)

    tour.guide = users_dao.get_user_by_id(tour.guide_id)
    tour.guide.languages = languages_dao.get_languages_by_user_id(tour.guide.id)
    theme=tour.theme.name.lower()   
    avaiable_days=days_to_numbers.days_to_numbers(tour)

    return render_template("tour.html", tour=tour, theme=theme, avaiable_days=avaiable_days, today=today)

# TOUR MANAGEMENT

#TODO: guides cannot create tours that overlap  with their tours
@app.route("/tours/new")
@login_required
@guide_required
def new_tour():

    languages=languages_dao.get_languages()
    themes=themes_dao.get_themes()

    return render_template("new_tour.html", languages=languages, themes=themes, origin="new")

@app.route("/tours/new", methods=["POST"])
@login_required
@guide_required
def new_tour_post():

    languages=languages_dao.get_languages()
    languages_names = []
    for language in languages:
        languages_names.append(language["name"])
    
    tour=request.form.to_dict()

    # title validation
    title=tour.get("title")
    if title in [None, ""]:
        flash("Invalid title", "negative")
        return redirect(url_for("new_tour"))
    elif len(title) < 2 or len(title) > 100:
        flash("Title must be between 2 and 100 characters", "negative")
        return redirect(url_for("new_tour"))

    # description validation
    description=tour.get("description")
    if description in [None, ""]:
        flash("Invalid description", "negative")
        return redirect(url_for("new_tour"))
    elif len(description) < 10 or len(description) > 1000:
        flash("Description must be between 10 and 1000 characters", "negative")
        return redirect(url_for("new_tour"))

    # duration validation
    duration=tour.get("duration")
    if duration in [None, ""]:
        flash("Invalid duration", "negative")
        return redirect(url_for("new_tour"))
    elif not duration.isdigit() or (int(duration) < 30 or int(duration) > 300):
        flash("Duration must be between 30 and 300", "negative")
        return redirect(url_for("new_tour"))
    duration=int(duration)

    # max participants validation
    max_participants=tour.get("max_participants")
    if max_participants in [None, ""]:
        flash("Invalid max participants", "negative")
        return redirect(url_for("new_tour"))
    elif not max_participants.isdigit() or int(max_participants) < 1:
        flash("Max participants must be a positive integer", "negative")
        return redirect(url_for("new_tour"))
    max_participants=int(max_participants)

    # language validation
    language=tour.get("language")
    if language in [None, ""]:
        flash("Invalid language", "negative")
        return redirect(url_for("new_tour"))
    if language not in languages_names:
        flash("Invalid language", "negative")
        return redirect(url_for("new_tour"))
    
    # theme validation
    theme=tour.get("theme")
    theme_obj=themes_dao.get_theme_by_name(theme)
    if theme in [None, ""]:
        flash("Invalid theme", "negative")
        return redirect(url_for("new_tour"))
    if theme_obj is None:
        flash("Invalid theme", "negative")
        return redirect(url_for("new_tour"))
    
    # schedule validation
    selected_days_dict = {"monday": None, "tuesday": None, "wednesday": None, "thursday": None, "friday": None, "saturday": None, "sunday": None}
    selected_days = request.form.getlist("days")
    if len(selected_days) == 0:
        flash("At least one day must be selected", "negative")
        return redirect(url_for("new_tour"))
    if len(selected_days) > 7:
        flash("Invalid number of days selected", "negative")
        return redirect(url_for("new_tour"))
    if not set(selected_days).issubset(set(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])):
        flash("Invalid days selected", "negative")
        return redirect(url_for("new_tour"))
    
    for day in selected_days:
        time = tour.get(day + "_time")
        if time in [None, ""]:
            flash("Invalid time for " + day, "negative")
            return redirect(url_for("new_tour"))
        if check_time.check_time(time) == False:
            flash("Invalid time for " + day, "negative")
            return redirect(url_for("new_tour"))
        selected_days_dict[day] = time
    
    # stops validation
    stops = request.form.getlist("stops")
    print(stops)
    if len(stops) < 4:
        flash("At least 4 stops must be added", "negative")
        return redirect(url_for("new_tour"))
    for stop in stops:
        if stop in [None, ""]:
            flash("Invalid stop", "negative")
            return redirect(url_for("new_tour"))
        if len(stop) < 2 or len(stop) > 20:
            flash("Stop must be between 2 and 20 characters", "negative")
            return redirect(url_for("new_tour"))
    
    photo1=request.files.get("photo1", None)
    photo2=request.files.get("photo2", None)
    photo3=request.files.get("photo3", None)
    photo4=request.files.get("photo4", None)
    photo5=request.files.get("photo5", None)
    photos = [photo1, photo2, photo3, photo4, photo5]

    for photo in photos:
        if (photo is None):
            flash("All 5 photos must be uploaded", "negative")
            return redirect(url_for("new_tour"))
        if (images.is_image(photo) == False):
            flash("One of the uploaded files is not an image", "negative")
            return redirect(url_for("new_tour"))
        if (images.is_16_9able(photo) == False):
            flash(f"One of the uploaded photos is too small and cannot be resized to 16:9, minimum size is {TOUR_PHOTO_IMG_WIDTH}x{TOUR_PHOTO_IMG_HEIGHT}", "negative")
            return redirect(url_for("new_tour"))

        extension=secure_filename(photo.filename).split(".")[-1].lower()
        photo_filename=str(uuid.uuid4()) + "." + extension
        photo.filename = photo_filename
        photo= images.to_16_9(photo)
        photo.save("static/images/tour_photos/" + photo_filename)
    photos = {"1": photo1.filename, "2": photo2.filename, "3": photo3.filename, "4": photo4.filename, "5": photo5.filename}

    # tour creation
    tour_obj=Tour(str(uuid.uuid4()), title, description, duration, max_participants)
    tour_obj.language = languages_dao.get_language_by_name(language)
    tour_obj.guide = current_user
    tour_obj.theme = theme_obj

    if not tours_dao.add_tour(tour_obj):
        flash("An error occurred, tour not created", "negative")
        return redirect(url_for("new_tour"))
    
    #add photos to database
    if not photos_dao.add_photos_to_tour(tour_obj, photos):
        flash("An error occurred, photos not added to tour", "negative")
        return redirect(url_for("new_tour"))

    #add stops to database
    if not stops_dao.add_stops_to_tour(tour_obj, stops):
        flash("An error occurred, stops not added to tour", "negative")
        return redirect(url_for("new_tour"))

    #add schedule to database
    if not tours_dao.add_schedule_to_tour(tour_obj, selected_days_dict):
        flash("An error occurred, schedule not added to tour", "negative")
        return redirect(url_for("new_tour"))
    
    flash("Tour created successfully", "positive")
    return redirect(url_for("tour", id=tour_obj.id))



#TODO: remove placeholder
@app.route("/tours/edit/<id>")
@login_required
@guide_required
def edit_tour(id):
    pass




@app.route("/tours/<id>/book")
@login_required
@participant_required
def book_tour(id):
    pass