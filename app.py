import os
from dotenv import load_dotenv

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from database.models import occurrence
from database.models.user import User
from database.models.tour import Tour
from database.models.theme import Theme
from database.models.occurrence import Occurrence
from database.models.reservation import Reservation
from database.models.extra_participant import Extra_Participant

from database.daos import reservations, users as users_dao
from database.daos import tours as tours_dao
from database.daos import themes as themes_dao
from database.daos import languages as languages_dao
from database.daos import photos as photos_dao
from database.daos import stops as stops_dao
from database.daos import occurrencies as occurrencies_dao
from database.daos import reservations as reservations_dao
from database.daos import extra_participants as extra_participants_dao

from utilities import check_date, check_email, check_password, images, days_to_numbers, check_time, date_to_day
from utilities.role_decorators import guide_required
from utilities.role_decorators import participant_required

from utilities.constants import PROFILE_IMG_HEIGHT, TOUR_PHOTO_IMG_HEIGHT, TOUR_PHOTO_IMG_WIDTH

import uuid
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date, datetime, timedelta



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
        return "Invalid email or password", 400
    
    # password validation
    password= user.get("password")
    if password in [None, ""]:
        return "Invalid password", 400

    if not user_obj.check_password(password):
        return "Invalid password", 400

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
    return redirect(url_for("profile", id=current_user.id))

@login_required
@app.route("/schedule")
def personal_schedule():

    today = date.today()

    if current_user.role == "guide":
        occurrences = occurrencies_dao.get_not_empty_occurrences_by_guide_id(current_user.id)
        for occurrence in occurrences:
            occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
            occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
            occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
        
        upcoming = occurrences
    else:
        reservations = reservations_dao.get_reservations_by_participant_id(current_user.id)
        occurrencies = []
        for reservation in reservations:
            occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
            occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
            occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
            occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
            occurrence.reservation = reservation
            occurrencies.append(occurrence)
        
        upcoming = occurrencies

    return render_template("personal_schedule.html", upcoming=upcoming)

@login_required
@app.route("/profile/<id>")
def profile(id):

    today = date.today()
    user = users_dao.get_user_by_id(id)
    
    if user.role == "guide":
        user.languages = languages_dao.get_languages_by_user_id(user.id)

        #get occurrences of the tours that the guide has created
        occurrences = occurrencies_dao.get_not_empty_occurrences_by_guide_id(user.id, limit=3, after_date=today)
        for occurrence in occurrences:
            occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
            occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
            occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
        
        upcoming = occurrences
        
        # get the tours that the guide has created, indipendently from the occurrences
        tours = tours_dao.get_tours_by_guide_id(user.id,6)
        for tour in tours:
            tour.photos=photos_dao.get_first_photo(tour)
            tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
            tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
            tour.stops=stops_dao.get_first_stop_by_tour(tour)
            tour.guide = users_dao.get_user_by_id(tour.guide_id)

            
    else:
        #get occurrences of the tours that the user has booked (the main focus is the occurrence, then we add the tour info)
        reservations = reservations_dao.get_reservations_by_participant_id(user.id, limit=3, after_date=today)
        occurrencies = []
        for reservation in reservations:
            occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
            occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
            occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
            occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
            occurrence.reservation = reservation
            occurrencies.append(occurrence)
        
        upcoming = occurrencies

        #get tours that the user has booked (the main focus is the tour, we need to pass through the occurrences to get the actual tours that the user has booked)
        temp_tours = []
        for reservation in reservations:
            occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
            
            tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            tour.photos=photos_dao.get_first_photo(tour)
            tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
            tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
            tour.stops=stops_dao.get_first_stop_by_tour(tour)
            tour.guide = users_dao.get_user_by_id(tour.guide_id)
            tour.occurrence_date = occurrence.date
            temp_tours.append(tour)

    
        #remove tour duplicates
        tours = []
        for tour in temp_tours:
            if len(tours) == 0:
                tours.append(tour)
            for temp in tours:
                if tour.id != temp.id:
                    tours.append(tour)
                    break
    
    return render_template("profile.html", upcoming=upcoming, tours=tours, user=user)

# TOUR LISTING

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

#TODO: implement filtering
@app.route("/tours/list")
def tours():

    today=date.today()
    
    tours=tours_dao.get_tours()

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

    has_active_reservations=reservations_dao.count_reservations_by_tour_id(tour.id, "active")
    has_reservations=reservations_dao.count_reservations_by_tour_id(tour.id)

    return render_template("tour.html", tour=tour, theme=theme, avaiable_days=avaiable_days, today=today, has_active_reservations=has_active_reservations, has_reservations=has_reservations)

# TOUR MANAGEMENT

@app.route("/tours/new")
@login_required
@guide_required
def new_tour():

    languages=languages_dao.get_languages_by_user_id(current_user.id)
    themes=themes_dao.get_themes()

    return render_template("new_tour.html", languages=languages, themes=themes, origin="new")

@app.route("/tours/new", methods=["POST"])
@login_required
@guide_required
def new_tour_post():

    languages=languages_dao.get_languages_by_user_id(current_user.id)
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


    # check overlap inside the tour
    checked_days = []

    for day in selected_days:
        time = selected_days_dict[day]

        for checked_day in checked_days:
            checked_time = selected_days_dict[checked_day]

            if check_time.check_week_overlap(day, time, duration, checked_day, checked_time, duration):
                flash("The selected times overlap each other", "negative")
                return redirect(url_for("new_tour"))

        checked_days.append(day)


    # check overlap with other tours of the guide
    temp_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    for day in selected_days:
        time = selected_days_dict[day]

        for temp_day in temp_days:
            tours_times_durations = tours_dao.get_times_and_duration_of_tours_by_guide_id_and_day(current_user.id, temp_day)

            for tour_time, tour_duration in tours_times_durations:
                if check_time.check_week_overlap(day, time, duration, temp_day, tour_time, tour_duration):
                    flash("The time you choose for " + day + " overlaps with another tour", "negative")
                    return redirect(url_for("new_tour"))

    # stops validation
    stops = request.form.getlist("stops")
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



@app.route("/tours/edit/<id>")
@login_required
@guide_required
def edit_tour(id):
    
    tour=tours_dao.get_tour_by_id(id)

    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if tour.guide_id != current_user.id:
        flash("You are not authorized to edit this tour", "negative")
        return redirect(url_for("home"))

    if tour.state != "active":
        flash("You cannot edit a tour that is not active", "negative")
        return redirect(url_for("home"))

    if reservations_dao.count_reservations_by_tour_id(tour.id) > 0:
        flash("You cannot edit a tour that had reservations", "negative")
        return redirect(url_for("home"))

    languages=languages_dao.get_languages_by_user_id(current_user.id)
    themes=themes_dao.get_themes()

    tour.language = languages_dao.get_language_by_id(tour.language_id)["name"]
    tour.theme = themes_dao.get_theme_by_id(tour.theme_id)
    tour.weekly_schedule=tours_dao.get_schedule_by_tour(tour)
    tour.stops = stops_dao.get_stops_by_tour(tour)

    return render_template("new_tour.html", languages=languages, themes=themes, tour=tour, origin="edit")

@app.route("/tours/edit/<id>", methods=["POST"])
@login_required
@guide_required
def edit_tour_post(id):
    
    tour_db=tours_dao.get_tour_by_id(id)

    # check ownership of the tour
    if tour_db is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if tour_db.guide_id != current_user.id:
        flash("You are not authorized to edit this tour", "negative")
        return redirect(url_for("home"))
    
    if tour_db.state != "active":
        flash("You cannot edit a tour that is not active", "negative")
        return redirect(url_for("home"))
    
    if reservations_dao.count_reservations_by_tour_id(tour_db.id) > 0:
        flash("You cannot edit a tour that had reservations", "negative")
        return redirect(url_for("home"))

    languages=languages_dao.get_languages_by_user_id(current_user.id)
    languages_names = []
    for language in languages:
        languages_names.append(language["name"])
    
    tour=request.form.to_dict()

    # title validation
    title=tour.get("title")
    if title in [None, ""]:
        flash("Invalid title", "negative")
        return redirect(url_for("edit_tour", id=id))
    elif len(title) < 2 or len(title) > 100:
        flash("Title must be between 2 and 100 characters", "negative")
        return redirect(url_for("edit_tour", id=id))

    # description validation
    description=tour.get("description")
    if description in [None, ""]:
        flash("Invalid description", "negative")
        return redirect(url_for("edit_tour", id=id))
    elif len(description) < 10 or len(description) > 1000:
        flash("Description must be between 10 and 1000 characters", "negative")
        return redirect(url_for("edit_tour", id=id))

    # duration validation
    duration=tour.get("duration")
    if duration in [None, ""]:
        flash("Invalid duration", "negative")
        return redirect(url_for("edit_tour", id=id))
    elif not duration.isdigit() or (int(duration) < 30 or int(duration) > 300):
        flash("Duration must be between 30 and 300", "negative")
        return redirect(url_for("edit_tour", id=id))
    duration=int(duration)

    # max participants validation
    max_participants=tour.get("max_participants")
    if max_participants in [None, ""]:
        flash("Invalid max participants", "negative")
        return redirect(url_for("edit_tour", id=id))
    elif not max_participants.isdigit() or int(max_participants) < 1:
        flash("Max participants must be a positive integer", "negative")
        return redirect(url_for("edit_tour", id=id))
    max_participants=int(max_participants)

    # language validation
    language=tour.get("language")
    if language in [None, ""]:
        flash("Invalid language", "negative")
        return redirect(url_for("edit_tour", id=id))
    if language not in languages_names:
        flash("Invalid language", "negative")
        return redirect(url_for("edit_tour", id=id))
    
    # theme validation
    theme=tour.get("theme")
    theme_obj=themes_dao.get_theme_by_name(theme)
    if theme in [None, ""]:
        flash("Invalid theme", "negative")
        return redirect(url_for("edit_tour", id=id))
    if theme_obj is None:
        flash("Invalid theme", "negative")
        return redirect(url_for("edit_tour", id=id))
    
    # schedule validation
    selected_days_dict = {"monday": None, "tuesday": None, "wednesday": None, "thursday": None, "friday": None, "saturday": None, "sunday": None}
    selected_days = request.form.getlist("days")
    if len(selected_days) == 0:
        flash("At least one day must be selected", "negative")
        return redirect(url_for("edit_tour", id=id))
    if len(selected_days) > 7:
        flash("Invalid number of days selected", "negative")
        return redirect(url_for("edit_tour", id=id))
    if not set(selected_days).issubset(set(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])):
        flash("Invalid days selected", "negative")
        return redirect(url_for("edit_tour", id=id))
    
    for day in selected_days:
        time = tour.get(day + "_time")
        if time in [None, ""]:
            flash("Invalid time for " + day, "negative")
            return redirect(url_for("edit_tour", id=id))
        if check_time.check_time(time) == False:
            flash("Invalid time for " + day, "negative")
            return redirect(url_for("edit_tour", id=id))
        selected_days_dict[day] = time


    # check overlap inside the tour
    checked_days = []

    for day in selected_days:
        time = selected_days_dict[day]

        for checked_day in checked_days:
            checked_time = selected_days_dict[checked_day]

            if check_time.check_week_overlap(day, time, duration, checked_day, checked_time, duration):
                flash("The selected times overlap each other", "negative")
                return redirect(url_for("edit_tour", id=id))

        checked_days.append(day)


    # check overlap with other tours of the guide
    temp_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    for day in selected_days:
        time = selected_days_dict[day]

        for temp_day in temp_days:
            tours_times_durations = tours_dao.get_times_and_duration_of_tours_by_guide_id_and_day_this_excluded(current_user.id, temp_day, tour_db.id)

            for tour_time, tour_duration in tours_times_durations:
                if check_time.check_week_overlap(day, time, duration, temp_day, tour_time, tour_duration):
                    flash("The time you choose for " + day + " overlaps with another tour", "negative")
                    return redirect(url_for("edit_tour", id=id))

    # stops validation
    stops = request.form.getlist("stops")
    if len(stops) < 4:
        flash("At least 4 stops must be added", "negative")
        return redirect(url_for("edit_tour", id=id))
    for stop in stops:
        if stop in [None, ""]:
            flash("Invalid stop", "negative")
            return redirect(url_for("edit_tour", id=id))
        if len(stop) < 2 or len(stop) > 20:
            flash("Stop must be between 2 and 20 characters", "negative")
            return redirect(url_for("edit_tour", id=id))

    # photos validation
    photo1=request.files.get("photo1", None)
    photo2=request.files.get("photo2", None)
    photo3=request.files.get("photo3", None)
    photo4=request.files.get("photo4", None)
    photo5=request.files.get("photo5", None)
    photos = [photo1, photo2, photo3, photo4, photo5]

    for photo in photos:
        
        if photo is not None and photo.filename != "":
            if (images.is_image(photo) == False):
                flash("One of the uploaded files is not an image", "negative")
                return redirect(url_for("edit_tour", id=id))
            if (images.is_16_9able(photo) == False):
                flash(f"One of the uploaded photos is too small and cannot be resized to 16:9, minimum size is {TOUR_PHOTO_IMG_WIDTH}x{TOUR_PHOTO_IMG_HEIGHT}", "negative")
                return redirect(url_for("edit_tour", id=id))

            extension=secure_filename(photo.filename).split(".")[-1].lower()
            photo_filename=str(uuid.uuid4()) + "." + extension
            photo.filename = photo_filename
            photo= images.to_16_9(photo)
            photo.save("static/images/tour_photos/" + photo_filename)

    # tour creation
    tour_obj=Tour(tour_db.id, title, description, duration, max_participants)
    tour_obj.language = languages_dao.get_language_by_name(language)
    tour_obj.guide = current_user
    tour_obj.theme = theme_obj

    if not tours_dao.update_tour(tour_obj):
        flash("An error occurred, tour not created", "negative")
        return redirect(url_for("edit_tour", id=id))
    
    #add photos to database
    old_photos = photos_dao.get_tour_photos(tour_obj)

    i=1
    for photo in photos:
        if photo is not None and photo.filename != "":
            if not photos_dao.update_photo_to_tour(tour_obj, i, photo.filename):
                flash("An error occurred, photos not added to tour", "negative")
                return redirect(url_for("edit_tour", id=id))
            if os.path.exists("static/images/tour_photos/" + old_photos[f"photo{i}"]):
                os.remove("static/images/tour_photos/" + old_photos[f"photo{i}"])
        i += 1

    #add stops to database
    if not stops_dao.update_stops_of_tour(tour_obj, stops):
        flash("An error occurred, stops not added to tour", "negative")
        return redirect(url_for("edit_tour", id=id))

    #add schedule to database
    if not tours_dao.update_tour_schedule(tour_obj, selected_days_dict):
        flash("An error occurred, schedule not added to tour", "negative")
        return redirect(url_for("edit_tour", id=id))
    
    flash("Tour edited successfully", "positive")
    return redirect(url_for("tour", id=tour_obj.id))

@app.route("/tours/delete/<id>", methods=["POST"])
@login_required
@guide_required
def delete_tour(id):
    tour=tours_dao.get_tour_by_id(id)

    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if tour.guide_id != current_user.id:
        flash("You are not authorized to delete this tour", "negative")
        return redirect(url_for("home"))

    if reservations_dao.count_reservations_by_tour_id(tour.id, "active") > 0:
        flash("You cannot edit a tour that has active reservations", "negative")
        return redirect(url_for("home"))
    
    if not tours_dao.update_tour_state(tour, "deleted"):
        flash("An error occurred, tour not deleted", "negative")
        return redirect(url_for("tour", id=id))
    
    flash("Tour deleted successfully", "positive")
    return redirect(url_for("home"))

# BOOKING MANAGEMENT

@app.route("/tours/<id>/book", methods=["POST"])
@login_required
@participant_required
def book_tour(id):
    
    tour=tours_dao.get_tour_by_id(id)
    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))

    if tour.state != "active":
        flash("This tour is not available for booking", "negative")
        return redirect(url_for("home"))
    
    reservation=request.form.to_dict()

    # date validation
    date= reservation.get("tour_date")
    if date in [None, ""]:
        flash("Invalid date", "negative")
        return redirect(url_for("tour", id=id))
    
    # DATE VALIDATION ONLY DATE PART
    date_obj, error_string = check_date.check_date(date)
    if date_obj is None:
        flash("Invalid date, " + error_string, "negative")
        return redirect(url_for("tour", id=id))
    
    # check if the tour is available on the selected date
    weekly_schedule=tours_dao.get_weekly_schedule_by_tour(tour)
    if weekly_schedule[date_to_day.date_to_day(date_obj)] is None:
        flash("The tour is not available on the selected date", "negative")
        return redirect(url_for("tour", id=id))

    #time recoveryng
    time = weekly_schedule[date_to_day.date_to_day(date_obj)]
    time_obj = datetime.strptime(time, "%H:%M").time()

    if time_obj < datetime.now().time() and date_obj == datetime.now().date():
        flash("Today the tour is departed yet", "negative")
        return redirect(url_for("tour", id=id))

    # verify if an occurrence already exists for the selected date and tour
    occurrence_obj=occurrencies_dao.get_occurrence_by_tour_and_date(tour.id, date_obj)
    if occurrence_obj is None:
        #occurrence creation
        occurrence_obj=Occurrence(str(uuid.uuid4()), tour.id, date_obj, time)
        if not occurrencies_dao.add_occurrence(occurrence_obj):
            flash("An error occurred, occurrence not created", "negative")
            return redirect(url_for("tour", id=id))
    occurrence_obj.tour = tour
    
    # check if the user has already booked the tour on the selected date
    reservation_obj=reservations_dao.get_active_reservation_by_participant_and_occurrence(current_user, occurrence_obj)
    if reservation_obj is not None:
        flash("You have already booked this tour on the selected date", "negative")
        return redirect(url_for("tour", id=id))

    #check overlap with other reservations

    #convert time to datetime for overlap check in case one tour ends after midnight
    new_start = datetime.combine(occurrence_obj.date,datetime.strptime(time, "%H:%M").time())
    new_end = new_start + timedelta(minutes=tour.duration)

    temp_reservations = reservations_dao.get_active_reservations_by_participant_id(current_user.id)
    for temp_reservation in temp_reservations:
        temp_occurrence = occurrencies_dao.get_occurrence_by_id(temp_reservation.occurrence_id)
        temp_tour = tours_dao.get_tour_by_id(temp_occurrence.tour_id)

        temp_start = datetime.combine(temp_occurrence.date,datetime.strptime(temp_occurrence.start_time, "%H:%M").time())
        temp_end = temp_start + timedelta(minutes=temp_tour.duration)

        if new_start < temp_end and new_end > temp_start:
            flash("You have already booked another tour that overlaps with this one", "negative")
            return redirect(url_for("tour", id=id))

    # participants validation
    participant_first_name_1 = reservation.get("participant_first_name_1")
    participant_last_name_1 = reservation.get("participant_last_name_1")
    participant_email_1 = reservation.get("participant_email_1")
    first_participant = Extra_Participant(str(uuid.uuid4()), participant_first_name_1, participant_last_name_1, participant_email_1)

    participant_first_name_2 = reservation.get("participant_first_name_2")
    participant_last_name_2 = reservation.get("participant_last_name_2")
    participant_email_2 = reservation.get("participant_email_2")
    second_participant = Extra_Participant(str(uuid.uuid4()), participant_first_name_2, participant_last_name_2, participant_email_2)

    participant_first_name_3 = reservation.get("participant_first_name_3")
    participant_last_name_3 = reservation.get("participant_last_name_3")
    participant_email_3 = reservation.get("participant_email_3")
    third_participant = Extra_Participant(str(uuid.uuid4()), participant_first_name_3, participant_last_name_3, participant_email_3)

    # participant number validation
    participant_number = request.form.get("people_count")
    if participant_number in [None, ""]:
        flash("Invalid number of participants", "negative")
        return redirect(url_for("tour", id=id))
    if not participant_number.isdigit() or int(participant_number) < 1 or int(participant_number) > 4:
        flash("Invalid number of participants", "negative")
        return redirect(url_for("tour", id=id))
    participant_number = int(participant_number)

    if participant_number > tour.max_participants:
        flash("The number of participants exceeds the maximum allowed for this tour", "negative")
        return redirect(url_for("tour", id=id))
    if participant_number + occurrencies_dao.get_participants_number(occurrence_obj) > tour.max_participants:
        flash("The number of participants exceeds the maximum allowed for this tour", "negative")
        return redirect(url_for("tour", id=id))

    participants= [first_participant, second_participant, third_participant]

    for i in range(participant_number-1):
        participant = participants[i]
        if participant.first_name in [None, ""]:
            flash("Invalid first name for participant " + str(i+1), "negative")
            return redirect(url_for("tour", id=id))
        if participant.last_name in [None, ""]:
            flash("Invalid last name for participant " + str(i+1), "negative")
            return redirect(url_for("tour", id=id))
        if participant.email in [None, ""]:
            flash("Invalid email for participant " + str(i+1), "negative")
            return redirect(url_for("tour", id=id))
        if check_email.check_email(participant.email) == False:
            flash("Invalid email for participant " + str(i+1), "negative")
            return redirect(url_for("tour", id=id))

    #reservation insertion
    reservation_obj=Reservation(str(uuid.uuid4()), current_user.id, occurrence_obj.id, datetime.now())

    if not reservations_dao.add_reservation(reservation_obj):
        flash("An error occurred, reservation not created", "negative")
        return redirect(url_for("tour", id=id))
    
    #participants insertion
    for i in range(participant_number-1):
        participants[i].reservation_id = reservation_obj.id
        if not extra_participants_dao.add_extra_participant(participants[i]):
            flash("An error occurred, participant " + str(i+1) + " not added", "negative")
            return redirect(url_for("tour", id=id))
        
    flash("Tour booked successfully", "positive")
    return redirect(url_for("my_profile"))

@app.route("/reservations/<id>")
@login_required
@participant_required
def reservation(id):

    #check ownership of the reservation
    reservation=reservations_dao.get_reservation_by_id(id)
    if reservation is None:
        flash("Reservation not found", "negative")
        return redirect(url_for("my_profile"))
    
    if reservation.participant_id != current_user.id:
        flash("You are not authorized to view this reservation", "negative")
        return redirect(url_for("my_profile"))
    
    #retrieving reservation data
    occurrence=occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
    if occurrence is None:
        flash("Occurrence not found", "negative")
        return redirect(url_for("my_profile"))
    
    occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
    if occurrence.tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("my_profile"))
    
    occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
    occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
    occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
    occurrence.tour.guide = users_dao.get_user_by_id(occurrence.tour.guide_id)

    reservation.occurrence = occurrence
    reservation.extra_participants = extra_participants_dao.get_extra_participants_by_reservation_id(reservation.id)
    number_of_participants = len(reservation.extra_participants) + 1

    #combine the occurrence date and time to get the actual tour datetime
    tour_datetime = datetime.combine(occurrence.date, datetime.strptime(occurrence.start_time, "%H:%M").time())

    cancelation_limit = tour_datetime - timedelta(days=1)
    seconds_remaining = int((cancelation_limit - datetime.now()).total_seconds())

    return render_template("reservation.html", reservation=reservation, cancelation_limit=cancelation_limit, seconds_remaining=seconds_remaining, number_of_participants=number_of_participants)

@app.route("/reservations/<id>/delete", methods=["POST"])
@login_required
@participant_required
def delete_reservation(id):
    
    #check ownership of the reservation
    reservation=reservations_dao.get_reservation_by_id(id)
    if reservation is None:
        flash("Reservation not found", "negative")
        return redirect(url_for("my_profile"))
    
    if reservation.participant_id != current_user.id:
        flash("You are not authorized to view this reservation", "negative")
        return redirect(url_for("my_profile"))
    
    #check if the reservation is already canceled
    if reservation.state == "canceled":
        flash("This reservation is already canceled", "negative")
        return redirect(url_for("reservation", id=id))
    
    #get occurrence because we need the date of the tour to check if it can be canceled
    occurrence=occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
    if occurrence is None:
        flash("Occurrence not found", "negative")
        return redirect(url_for("my_profile"))
    
    #compute the exact datetime 
    tour_datetime = datetime.combine(occurrence.date, datetime.strptime(occurrence.start_time, "%H:%M").time())
    
    # check if the reservation is cancellable
    if datetime.now() > tour_datetime - timedelta(days=1):
        flash("The reservation cannot be canceled less than 24 hours before the tour", "negative")
        return redirect(url_for("reservation", id=id))
    

    if not reservations_dao.update_reservation_state(reservation.id, "canceled"):
        flash("An error occurred, reservation not canceled", "negative")
        return redirect(url_for("reservation", id=id))
    
    flash("Reservation canceled successfully", "positive")
    return redirect(url_for("my_profile"))
