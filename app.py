import os
from dotenv import load_dotenv

from flask import Flask, flash, redirect, render_template, request, url_for, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from database.models.user import User
from database.models.tour import Tour
from database.models.theme import Theme
from database.models.occurrence import Occurrence
from database.models.reservation import Reservation
from database.models.extra_participant import Extra_Participant
from database.models.report import Report
from database.models.review import Review

from database.daos import users as users_dao
from database.daos import tours as tours_dao
from database.daos import themes as themes_dao
from database.daos import languages as languages_dao
from database.daos import photos as photos_dao
from database.daos import stops as stops_dao
from database.daos import occurrencies as occurrencies_dao
from database.daos import reservations as reservations_dao
from database.daos import extra_participants as extra_participants_dao
from database.daos import reports as reports_dao
from database.daos import admins as admins_dao
from database.daos import reviews as reviews_dao
from database.daos import logs as logs_dao

from utilities import check_date, check_email, check_password, images, days_to_numbers, check_time, date_to_day
from utilities.role_decorators import guide_required
from utilities.role_decorators import participant_required

from utilities.constants import (
    PROFILE_IMG_HEIGHT,
    TOUR_PHOTO_IMG_HEIGHT,
    TOUR_PHOTO_IMG_WIDTH,
    TOUR_TITLE_MIN_LENGTH,
    TOUR_TITLE_MAX_LENGTH,
    TOUR_DESCRIPTION_MIN_LENGTH,
    TOUR_DESCRIPTION_MAX_LENGTH,
    TOUR_DURATION_MIN_MINUTES,
    TOUR_DURATION_MAX_MINUTES,
    STOP_MIN_LENGTH,
    STOP_MAX_LENGTH,
    REVIEW_COMMENT_MIN_LENGTH,
    REVIEW_COMMENT_MAX_LENGTH,
)

import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import date, datetime, timedelta
from ics import Calendar, Event
from zoneinfo import ZoneInfo


#load everythings from .env file
load_dotenv()

app=Flask(__name__)
app.config["SECRET_KEY"]=os.getenv("APP-SECRET-KEY")  #loads the key from .env

login_manager= LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    flash("You need to log in to access this page.", "negative")
    return redirect(url_for("login"))


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
        flash("Invalid role", "negative")
        return redirect(url_for("register"))
    if role not in ["participant","guide"]:
        flash("Invalid role", "negative")
        return redirect(url_for("register"))
    
    #email validation
    email= user.get("email")
    if email in [None, ""]:
        flash("Invalid email", "negative")
        return redirect(url_for("register"))
    if check_email.check_email(email) == False:
        flash("Invalid email", "negative")
        return redirect(url_for("register"))
    if users_dao.get_user_by_email(email):
        flash("User already registered", "negative")
        return redirect(url_for("register"))

    # password validation
    password= user.get("password")
    if password in [None, ""]:
        flash("Invalid password", "negative")
        return redirect(url_for("register"))
    if check_password.check_password(password) == False:
        flash("Invalid password", "negative")
        return redirect(url_for("register"))
    password=generate_password_hash(password)

    # First name validation
    first_name= user.get("first_name")
    if first_name in [None, ""]:
        flash("Invalid first name", "negative")
        return redirect(url_for("register"))

    # Last name validation
    last_name= user.get("last_name")
    if last_name in [None, ""]:
        flash("Invalid last name", "negative")
        return redirect(url_for("register"))

    #image validartion
    profile_photo= request.files.get("profile_photo", None)
    profile_photo_filename = None
    if profile_photo:

        #file type verification
        if not images.is_image(profile_photo):
            flash("Invalid profile photo", "negative")
            return redirect(url_for("register"))
        if not images.is_squareable(profile_photo):
            flash(f"Invalid profile photo, must be squareable, minimum size is {PROFILE_IMG_HEIGHT}x{PROFILE_IMG_HEIGHT}", "negative")
            return redirect(url_for("register"))

        #file naming
        extension=secure_filename(profile_photo.filename).split(".")[-1].lower()
        profile_photo_filename=str(uuid.uuid4()) + "." + extension

        #image resizing
        profile_photo= images.to_square(profile_photo)

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
            flash("Invalid languages", "negative")
            return redirect(url_for("register"))
        
        guide_languages = []

        for language in available_languages:
            if language["name"] in selected_languages:
                guide_languages.append(language)
        
        if len(selected_languages) == 0:
            flash("At least one language must be selected for guides", "negative")
            return redirect(url_for("register"))
    else:
        guide_languages = None

    user_obj=User(id, role, email, password, first_name, last_name, profile_photo_filename)

    if not users_dao.add_user(user_obj):
        flash("An error occurred, user not registered", "negative")
        return redirect(url_for("register"))

    if guide_languages is not None:
        if not languages_dao.add_language_to_user(user_obj, guide_languages):
            flash("An error occurred, languages not added", "negative")
            return redirect(url_for("register"))

    login_user(user_obj)
    flash("Registration successful", "positive")

    logs_dao.add_log(f"Registration successful by user ID {current_user.id}")
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
        flash("Invalid email", "negative")
        return redirect(url_for("login"))
    if check_email.check_email(email) == False:
        flash("Invalid email", "negative")
        return redirect(url_for("login"))
    
    user_obj=users_dao.get_user_by_email(email)

    if user_obj is None:
        flash("Invalid email or password", "negative")
        return redirect(url_for("login"))
    
    # password validation
    password= user.get("password")
    if password in [None, ""]:
        flash("Invalid password", "negative")
        return redirect(url_for("login"))

    if not user_obj.check_password(password):
        flash("Invalid password", "negative")
        return redirect(url_for("login"))

    login_user(user_obj)

    logs_dao.add_log(f"Login successful by user ID {current_user.id}")
    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    user_id = current_user.id
    logout_user()

    logs_dao.add_log(f"Logout by user ID {user_id}")
    return redirect(url_for("home"))


@app.route("/register")
def register():
    if current_user.is_authenticated:
        flash("You are already logged in", "negative")
        return redirect(url_for("home"))

    languages=languages_dao.get_languages()

    return render_template("register.html", languages=languages, origin="new", selected_language_names=[])

@app.route("/login")
def login():

    if current_user.is_authenticated:
        flash("You are already logged in", "negative")
        return redirect(url_for("home"))

    return render_template("login.html")


# NON-AUTH ROUTES

@app.route("/me")
@login_required
def my_profile():
    return redirect(url_for("profile", id=current_user.id))

@app.route("/schedule")
@login_required
def personal_schedule():


    # guides and participants need different queries, but the template always receives upcoming
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

    return render_template("personal_schedule.html", upcoming=upcoming, user=current_user)

@app.route("/profile/edit")
@login_required
def edit_profile():

    languages=languages_dao.get_languages()
    selected_language_names = []

    if current_user.role == "guide":
        user_languages=languages_dao.get_languages_by_user_id(current_user.id)

        for language in user_languages:
            selected_language_names.append(language["name"])

    return render_template("register.html", user=current_user, languages=languages, selected_language_names=selected_language_names, origin="edit")

@app.route("/profile/edit", methods=["POST"])
@login_required
def edit_profile_post():

    user=request.form.to_dict()

    #email validation
    email= user.get("email")
    if email in [None, ""]:
        flash("Invalid email", "negative")
        return redirect(url_for("edit_profile"))
    if check_email.check_email(email) == False:
        flash("Invalid email", "negative")
        return redirect(url_for("edit_profile"))
    user_db=users_dao.get_user_by_email(email)
    if user_db is not None and user_db.id != current_user.id:
        flash("Email taken from another user", "negative")
        return redirect(url_for("edit_profile"))

    # password validation
    password= user.get("password")
    if password not in [None, ""]:
        if check_password.check_password(password) == False:
            flash("Invalid password", "negative")
            return redirect(url_for("edit_profile"))
        password=generate_password_hash(password)
    else:
        password=current_user.password

    # First name validation
    first_name= user.get("first_name")
    if first_name in [None, ""]:
        flash("Invalid first name", "negative")
        return redirect(url_for("edit_profile"))

    # Last name validation
    last_name= user.get("last_name")
    if last_name in [None, ""]:
        flash("Invalid last name", "negative")
        return redirect(url_for("edit_profile"))

    #image validation
    profile_photo= request.files.get("profile_photo", None)
    remove_profile_photo = user.get("remove_profile_photo")
    if remove_profile_photo == "on":
        profile_photo_filename=None
    elif profile_photo:

        #file type verification
        if not images.is_image(profile_photo):
            flash("Invalid profile photo", "negative")
            return redirect(url_for("edit_profile"))
        if not images.is_squareable(profile_photo):
            flash(f"Invalid profile photo, must be squareable, minimum size is {PROFILE_IMG_HEIGHT}x{PROFILE_IMG_HEIGHT}", "negative")
            return redirect(url_for("edit_profile"))

        #file naming
        extension=secure_filename(profile_photo.filename).split(".")[-1].lower()
        profile_photo_filename=str(uuid.uuid4()) + "." + extension

        #image resizing
        profile_photo= images.to_square(profile_photo)

        profile_photo.save("static/images/profile_photos/" + profile_photo_filename)
    else:
        profile_photo_filename=current_user.profile_photo

    #languages validation
    if current_user.role == "guide":
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
            flash("Invalid languages", "negative")
            return redirect(url_for("edit_profile"))

        guide_languages = []

        for language in available_languages:
            if language["name"] in selected_languages:
                guide_languages.append(language)

        if len(selected_languages) == 0:
            flash("At least one language must be selected for guides", "negative")
            return redirect(url_for("edit_profile"))

        # guides cannot remove languages still used by their active tours
        guide_tours = tours_dao.get_tours_by_guide_id(current_user.id, state="active")
        selected_language_ids = []
        for language in guide_languages:
            selected_language_ids.append(str(language["id"]))

        for tour in guide_tours:
            if str(tour.language_id) not in selected_language_ids:
                flash("You cannot remove languages used by your active tours", "negative")
                return redirect(url_for("edit_profile"))
    else:
        guide_languages = None

    user_obj=User(current_user.id, current_user.role, email, password, first_name, last_name, profile_photo_filename)

    if not users_dao.update_user(user_obj):
        flash("An error occurred, profile not edited", "negative")
        return redirect(url_for("edit_profile"))

    if guide_languages is not None:
        if not languages_dao.update_languages_of_user(user_obj, guide_languages):
            flash("An error occurred, languages not edited", "negative")
            return redirect(url_for("edit_profile"))

    

    flash("Profile edited successfully", "positive")
    logs_dao.add_log(f"Profile edited successfully by user ID {current_user.id}")
    return redirect(url_for("my_profile"))

@app.route("/profile/<id>")
@login_required
def profile(id):

    today = date.today()
    user = users_dao.get_user_by_id(id)
    if user is None:
        flash("User not found", "negative")
        return redirect(url_for("home"))
    
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
        tours = tours_dao.get_tours_by_guide_id(user.id, limit=3)
        for tour in tours:
            tour.photos=photos_dao.get_first_photo(tour)
            tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
            tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
            tour.stops=stops_dao.get_first_stop_by_tour(tour)
            tour.guide = users_dao.get_user_by_id(tour.guide_id)

            
    else:
        #get occurrences and tours that the user has booked
        reservations = reservations_dao.get_reservations_by_participant_id(user.id, limit=3, after_date=today)
        occurrencies = []
        temp_tours = []
        for reservation in reservations:
            occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)

            tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            tour.photos=photos_dao.get_first_photo(tour)
            tour.language = languages_dao.get_language_by_id(tour.language_id)["name"]
            tour.theme = themes_dao.get_theme_by_id(tour.theme_id)
            tour.stops = stops_dao.get_first_stop_by_tour(tour)
            tour.guide = users_dao.get_user_by_id(tour.guide_id)
            tour.occurrence_date = occurrence.date

            occurrence.tour = tour
            occurrence.reservation = reservation
            
            occurrencies.append(occurrence)
            temp_tours.append(tour)
        
        upcoming = occurrencies


    
        #remove tour duplicates
        tours = []
        for tour in temp_tours:
            already_present = False
            for temp in tours:
                if tour.id == temp.id:
                    already_present = True
                    break
            if not already_present:
                tours.append(tour)
    
    return render_template("profile.html", upcoming=upcoming, tours=tours, user=user)

# TOUR LISTING

@app.route("/")
def home():

    today=date.today()

    languages=languages_dao.get_languages()
    themes=themes_dao.get_themes()

    photo=photos_dao.get_random_photo()
    
    tours=tours_dao.get_tours_filters(limit=8, state="active")

    for tour in tours:
        tour.photos=photos_dao.get_first_photo(tour)
        tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
        tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
        tour.stops=stops_dao.get_first_stop_by_tour(tour)
        tour.guide = users_dao.get_user_by_id(tour.guide_id)

    return render_template("home.html", today=today, tours=tours, languages=languages, themes=themes, photo=photo)

@app.route("/tours/list")
def tours():

    today=date.today()

    # date check and filtering
    weekday = None
    start_date = request.args.get("start_date")
    date_range_check = request.args.get("date_range_check")
    if start_date is not None:

        weekday = []

        if start_date == "":
            flash("Invalid start date", "negative")
            return redirect(url_for("home"))

        start_date_obj, error_string = check_date.check_date(start_date)
        if start_date_obj is None:
            flash("Invalid start date, " + error_string, "negative")
            return redirect(url_for("home"))

        if date_range_check is None:
            weekday.append(date_to_day.date_to_day(start_date_obj))
        else:
            end_date = request.args.get("end_date")
            if end_date in [None, ""]:
                flash("Invalid end date", "negative")
                return redirect(url_for("home"))

            end_date_obj, error_string = check_date.check_date(end_date)
            if end_date_obj is None:
                flash("Invalid end date, " + error_string, "negative")
                return redirect(url_for("home"))
            if end_date_obj < start_date_obj:
                flash("End date must be after start date", "negative")
                return redirect(url_for("home"))

            # keep only distinct weekdays, because the dao filters weekly schedules
            weekday = []
            temp_date = start_date_obj
            while temp_date <= end_date_obj:
                temp_weekday = date_to_day.date_to_day(temp_date)
                if temp_weekday not in weekday:
                    weekday.append(temp_weekday)
                temp_date += timedelta(days=1)

    # duration check and filtering
    duration_allowed = ["0 - 1:30 h", "1:30 - 3 h", "3 h +"]
    duration = request.args.get("duration", "Any duration")
    if duration not in duration_allowed:
        if duration == "Any duration":
            duration = (0, None)
        else:
            flash("Invalid duration", "negative")
            return redirect(url_for("home"))
    elif duration == "0 - 1:30 h":
        duration = (0, 90)
    elif duration == "1:30 - 3 h":
        duration = (90, 180)
    elif duration == "3 h +":
        duration = (180, None)
    
    # language check and filtering
    languages=languages_dao.get_languages()
    languages_names = []
    for language in languages:
        languages_names.append(language["name"])
    language = request.args.get("language", "Any language")
    if language not in languages_names:
        if language == "Any language":
            language = None
        else:
            flash("Invalid language", "negative")
            return redirect(url_for("home"))
    else:
        language_db = languages_dao.get_language_by_name(language)
        language = language_db["id"]

    # theme check and filtering
    themes=themes_dao.get_themes()
    themes_names = []
    for theme in themes:
        themes_names.append(theme.name)
    theme = request.args.get("theme", "Any theme")
    if theme not in themes_names:
        if theme == "Any theme":
            theme = None
        else:
            flash("Invalid theme", "negative")
            return redirect(url_for("home"))
    else:
        theme_obj = themes_dao.get_theme_by_name(theme)
        theme = theme_obj.id

    # max participants check and filtering
    max_participants = request.args.get("maxPeople")
    if max_participants is not None and max_participants != "":
        if not max_participants.isdigit() or int(max_participants) < 1:
            flash("Max participants must be a positive integer", "negative")
            return redirect(url_for("home"))
        max_participants = int(max_participants)
    else:
        max_participants = None

    # min participants check and filtering
    min_participants = request.args.get("minPeople")
    if min_participants is not None and min_participants != "":
        if not min_participants.isdigit() or int(min_participants) < 1:
            flash("Min participants must be a positive integer", "negative")
            return redirect(url_for("home"))
        min_participants = int(min_participants)
    else:
        min_participants = None


    tours=tours_dao.get_tours_filters(state="active", weekday=weekday, duration_start=duration[0], duration_end=duration[1], language=language, theme=theme, max_participants=max_participants, min_participants=min_participants)

    for tour in tours:
        tour.photos=photos_dao.get_first_photo(tour)
        tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
        tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
        tour.stops=stops_dao.get_first_stop_by_tour(tour)
        tour.guide = users_dao.get_user_by_id(tour.guide_id)

    return render_template("tours.html", today=today, tours=tours, languages=languages, themes=themes, origin="list")

@app.route("/tour/<id>")
def tour(id):

    today=date.today()

    tour=tours_dao.get_tour_by_id(id)
    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))

    tour.theme = themes_dao.get_theme_by_id(tour.theme_id)
    tour.language = languages_dao.get_language_by_id(tour.language_id)
    tour.weekly_schedule=tours_dao.get_weekly_schedule_by_tour(tour)
    tour.photos=photos_dao.get_tour_photos(tour)
    tour.stops=stops_dao.get_stops_by_tour(tour)

    tour.guide = users_dao.get_user_by_id(tour.guide_id)
    tour.guide.languages = languages_dao.get_languages_by_user_id(tour.guide.id)
    theme=tour.theme.name.lower()   
    avaiable_days=days_to_numbers.days_to_numbers(tour)

    has_active_reservations=reservations_dao.count_reservations_by_tour_id(tour.id, "active", today)
    has_reservations=reservations_dao.count_reservations_by_tour_id(tour.id)

    #reviews management
    reviews=reviews_dao.get_reviews_by_tour_id(tour.id)

    user_review=None
    if current_user.is_authenticated and current_user.role == "participant":
        user_review=reviews_dao.get_review_by_participant_id_and_tour_id(current_user.id, tour.id)

    for review in reviews:
        review.participant = users_dao.get_user_by_id(review.participant_id)

    times_user_reserved=0
    if current_user.is_authenticated and current_user.role == "participant":
        times_user_reserved=reservations_dao.count_active_passed_reservations_by_participant_id_and_tour_id(current_user.id, tour.id, today)

    return render_template("tour.html", tour=tour, theme=theme, avaiable_days=avaiable_days, today=today, has_active_reservations=has_active_reservations, has_reservations=has_reservations, reviews=reviews, user_review=user_review, times_user_reserved=times_user_reserved)

@app.route("/tours/<user_id>")
def user_tours(user_id):

    user = users_dao.get_user_by_id(user_id)
    if user is None:
        flash("User not found", "negative")
        return redirect(url_for("home"))
    
    if user.role == "guide":
            user.languages = languages_dao.get_languages_by_user_id(user.id)

            #get occurrences of the tours that the guide has created
            occurrences = occurrencies_dao.get_not_empty_occurrences_by_guide_id(user.id)
            for occurrence in occurrences:
                occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
                occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
                occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
                occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
            
            
            # get the tours that the guide has created, indipendently from the occurrences
            tours = tours_dao.get_tours_by_guide_id(user.id,6)
            for tour in tours:
                tour.photos=photos_dao.get_first_photo(tour)
                tour.language=languages_dao.get_language_by_id(tour.language_id)["name"]
                tour.theme=themes_dao.get_theme_by_id(tour.theme_id)
                tour.stops=stops_dao.get_first_stop_by_tour(tour)
                tour.guide = users_dao.get_user_by_id(tour.guide_id)

            
    else:
        #get the tours that the user has booked
        reservations = reservations_dao.get_reservations_by_participant_id(user.id)
        temp_tours = []
        for reservation in reservations:
            occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)

            tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            tour.photos=photos_dao.get_first_photo(tour)
            tour.language = languages_dao.get_language_by_id(tour.language_id)["name"]
            tour.theme = themes_dao.get_theme_by_id(tour.theme_id)
            tour.stops = stops_dao.get_first_stop_by_tour(tour)
            tour.guide = users_dao.get_user_by_id(tour.guide_id)
            tour.occurrence_date = occurrence.date

            occurrence.tour = tour
            occurrence.reservation = reservation
            
            temp_tours.append(tour)


    
        #remove tour duplicates
        tours = []
        for tour in temp_tours:
            already_present = False
            for temp in tours:
                if tour.id == temp.id:
                    already_present = True
                    break
            if not already_present:
                tours.append(tour)
    
    return render_template("tours.html", tours=tours, user=user, origin="user_tours")

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
    elif len(title) < TOUR_TITLE_MIN_LENGTH or len(title) > TOUR_TITLE_MAX_LENGTH:
        flash(f"Title must be between {TOUR_TITLE_MIN_LENGTH} and {TOUR_TITLE_MAX_LENGTH} characters", "negative")
        return redirect(url_for("new_tour"))

    # description validation
    description=tour.get("description")
    if description in [None, ""]:
        flash("Invalid description", "negative")
        return redirect(url_for("new_tour"))
    elif len(description) < TOUR_DESCRIPTION_MIN_LENGTH or len(description) > TOUR_DESCRIPTION_MAX_LENGTH:
        flash(f"Description must be between {TOUR_DESCRIPTION_MIN_LENGTH} and {TOUR_DESCRIPTION_MAX_LENGTH} characters", "negative")
        return redirect(url_for("new_tour"))

    # duration validation
    duration=tour.get("duration")
    if duration in [None, ""]:
        flash("Invalid duration", "negative")
        return redirect(url_for("new_tour"))
    elif not duration.isdigit() or (int(duration) < TOUR_DURATION_MIN_MINUTES or int(duration) > TOUR_DURATION_MAX_MINUTES):
        flash(f"Duration must be between {TOUR_DURATION_MIN_MINUTES} and {TOUR_DURATION_MAX_MINUTES}", "negative")
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
    # inactive days stay None, so the dao always receives all week days
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


    # check overlap inside the tour, also if a tour ends on the next day
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
        if len(stop) < STOP_MIN_LENGTH or len(stop) > STOP_MAX_LENGTH:
            flash(f"Stop must be between {STOP_MIN_LENGTH} and {STOP_MAX_LENGTH} characters", "negative")
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
    logs_dao.add_log(f"Tour created successfully by user ID {current_user.id}")
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
    tour.weekly_schedule=tours_dao.get_weekly_schedule_by_tour(tour)
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

    # tours with reservations are locked because edits would change existing bookings
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
    elif len(title) < TOUR_TITLE_MIN_LENGTH or len(title) > TOUR_TITLE_MAX_LENGTH:
        flash(f"Title must be between {TOUR_TITLE_MIN_LENGTH} and {TOUR_TITLE_MAX_LENGTH} characters", "negative")
        return redirect(url_for("edit_tour", id=id))

    # description validation
    description=tour.get("description")
    if description in [None, ""]:
        flash("Invalid description", "negative")
        return redirect(url_for("edit_tour", id=id))
    elif len(description) < TOUR_DESCRIPTION_MIN_LENGTH or len(description) > TOUR_DESCRIPTION_MAX_LENGTH:
        flash(f"Description must be between {TOUR_DESCRIPTION_MIN_LENGTH} and {TOUR_DESCRIPTION_MAX_LENGTH} characters", "negative")
        return redirect(url_for("edit_tour", id=id))

    # duration validation
    duration=tour.get("duration")
    if duration in [None, ""]:
        flash("Invalid duration", "negative")
        return redirect(url_for("edit_tour", id=id))
    elif not duration.isdigit() or (int(duration) < TOUR_DURATION_MIN_MINUTES or int(duration) > TOUR_DURATION_MAX_MINUTES):
        flash(f"Duration must be between {TOUR_DURATION_MIN_MINUTES} and {TOUR_DURATION_MAX_MINUTES}", "negative")
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
    # inactive days stay None, so the dao always receives all week days
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


    # check overlap inside the tour, also if a tour ends on the next day
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
        if len(stop) < STOP_MIN_LENGTH or len(stop) > STOP_MAX_LENGTH:
            flash(f"Stop must be between {STOP_MIN_LENGTH} and {STOP_MAX_LENGTH} characters", "negative")
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
    # empty photo fields keep old images, uploaded ones replace only that position

    i=1
    for photo in photos:
        if photo is not None and photo.filename != "":
            if not photos_dao.update_photo_to_tour(tour_obj, i, photo.filename):
                flash("An error occurred, photos not added to tour", "negative")
                return redirect(url_for("edit_tour", id=id))
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
    logs_dao.add_log(f"Tour edited successfully by user ID {current_user.id}")
    return redirect(url_for("tour", id=tour_obj.id))

@app.route("/tours/delete/<id>", methods=["POST"])
@login_required
@guide_required
def delete_tour(id):

    today = date.today()

    tour=tours_dao.get_tour_by_id(id)

    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if tour.guide_id != current_user.id:
        flash("You are not authorized to delete this tour", "negative")
        return redirect(url_for("home"))

    if reservations_dao.count_reservations_by_tour_id(tour.id, "active", today) > 0:
        flash("You cannot edit a tour that has active reservations", "negative")
        return redirect(url_for("home"))
    
    if not tours_dao.update_tour_state(tour, "deleted"):
        flash("An error occurred, tour not deleted", "negative")
        return redirect(url_for("tour", id=id))
    
    flash("Tour deleted successfully", "positive")
    logs_dao.add_log(f"Tour deleted successfully by user ID {current_user.id}")
    return redirect(url_for("home"))


@app.route("/tours/<id>/review", methods=["POST"])
@login_required
@participant_required
def add_review(id):

    today = date.today()

    #verify if the user has a reservation for the tour
    tour=tours_dao.get_tour_by_id(id)
    if tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if reservations_dao.count_active_passed_reservations_by_participant_id_and_tour_id(current_user.id, tour.id, today) == 0:
        flash("You cannot review a tour you haven't booked", "negative")
        return redirect(url_for("home"))
    
    #verify if the user has already reviewed the tour
    if reviews_dao.get_review_by_participant_id_and_tour_id(current_user.id, tour.id) is not None:
        flash("You have already reviewed this tour", "negative")
        return redirect(url_for("home"))
    
    # rating validation
    rating=request.form.get("rating")
    if rating in [None, ""]:
        flash("Invalid rating", "negative")
        return redirect(url_for("tour", id=id))
    if not rating.isdigit():
        flash("Invalid rating", "negative")
        return redirect(url_for("tour", id=id))
    rating=int(rating)
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5", "negative")
        return redirect(url_for("tour", id=id))
    
    # comment validation
    comment=request.form.get("comment")
    if comment in [None, ""]:
        flash("Invalid comment", "negative")
        return redirect(url_for("tour", id=id))
    if len(comment) < REVIEW_COMMENT_MIN_LENGTH or len(comment) > REVIEW_COMMENT_MAX_LENGTH:
        flash(f"Comment must be between {REVIEW_COMMENT_MIN_LENGTH} and {REVIEW_COMMENT_MAX_LENGTH} characters", "negative")
        return redirect(url_for("tour", id=id))
    
    review=Review(str(uuid.uuid4()), tour.id, current_user.id, rating, comment)

    if not reviews_dao.add_review(review):
        flash("An error occurred, review not added", "negative")
        return redirect(url_for("tour", id=id))
    
    flash("Review added successfully", "positive")
    logs_dao.add_log(f"Review added successfully by user ID {current_user.id}")
    return redirect(url_for("tour", id=id))

# OCCURRENCE MANAGEMENT FOR GUIDES

@app.route("/occurrences/<id>")
@login_required
@guide_required
def occurrence_details(id):

    occurrence=occurrencies_dao.get_occurrence_by_id(id)
    if occurrence is None:
        flash("Occurrence not found", "negative")
        return redirect(url_for("home"))
    
    occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
    if occurrence.tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if occurrence.tour.guide_id != current_user.id:
        flash("You are not authorized to view this occurrence", "negative")
        return redirect(url_for("home"))
    
    occurrence.tour.language = languages_dao.get_language_by_id(occurrence.tour.language_id)["name"]
    occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)
    occurrence.tour.stops = stops_dao.get_first_stop_by_tour(occurrence.tour)
    occurrence.tour.theme = themes_dao.get_theme_by_id(occurrence.tour.theme_id)

    # template groups each reservation with the registered user and extra participants
    participants = []
    participants_number = 0

    reservations = reservations_dao.get_active_reservations_by_occurrence_id(occurrence.id)
    for reservation in reservations:
        temp = {}
        participant = users_dao.get_user_by_id(reservation.participant_id)
        temp["Registered"] = participant
        participants_number = participants_number + 1
        extra_participants = extra_participants_dao.get_extra_participants_by_reservation_id(reservation.id)
        temp["Extra"] = []
        i=0
        for extra_participant in extra_participants:
            temp["Extra"].append(extra_participant)
            i = i + 1
            participants_number = participants_number + 1
        participants.append(temp)

    tour_datetime = datetime.combine(occurrence.date, datetime.strptime(occurrence.start_time, "%H:%M").time())
    seconds_remaining = int((tour_datetime - datetime.now()).total_seconds())

    report = reports_dao.get_report_by_occurrence_id(occurrence.id)

    return render_template("occurrence_guide.html", occurrence=occurrence, participants=participants, participants_number=participants_number, seconds_remaining=seconds_remaining, report=report)

@app.route("/occurrences/<id>/calendar")
@login_required
@guide_required
def add_occurrence_to_calendar(id):

    zone = ZoneInfo("Europe/Rome")
    
    #check ownership of the occurrence
    occurrence=occurrencies_dao.get_occurrence_by_id(id)
    if occurrence is None:
        flash("Occurrence not found", "negative")
        return redirect(url_for("my_profile"))
    
    occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
    if occurrence.tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("my_profile"))


    if occurrence.tour.guide_id != current_user.id:
        flash("You are not authorized to view this occurrence", "negative")
        return redirect(url_for("my_profile"))
    

    calendar = Calendar()
    event = Event()

    event.name = occurrence.tour.title
    start_datetime = datetime.combine(occurrence.date, datetime.strptime(occurrence.start_time, "%H:%M").time(), tzinfo=zone)
    end_datetime = start_datetime + timedelta(minutes=occurrence.tour.duration)
    event.begin = start_datetime
    event.end = end_datetime

    calendar.events.add(event)

    response = Response(calendar.serialize(), mimetype='text/calendar')

    return response
    

@app.route("/occurrences/<id>/report", methods=["POST"])
@login_required
@guide_required
def submit_report(id):
    
    occurrence=occurrencies_dao.get_occurrence_by_id(id)
    if occurrence is None:
        flash("Occurrence not found", "negative")
        return redirect(url_for("home"))
    
    occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
    if occurrence.tour is None:
        flash("Tour not found", "negative")
        return redirect(url_for("home"))
    
    if occurrence.tour.guide_id != current_user.id:
        flash("You are not authorized to view this occurrence", "negative")
        return redirect(url_for("home"))
    
    if reports_dao.get_report_by_occurrence_id(occurrence.id) is not None:
        flash("A report has already been submitted for this occurrence", "negative")
        return redirect(url_for("occurrence_details", id=id))
    
    #check if the occurrence happened
    tour_datetime = datetime.combine(occurrence.date, datetime.strptime(occurrence.start_time, "%H:%M").time())
    if tour_datetime > datetime.now():
        flash("This occurrence has not happened yet", "negative")
        return redirect(url_for("occurrence_details", id=id))

    # number validation
    participants_number = request.form.get("effectiveParticipants")
    if participants_number in [None, ""]:
        flash("Invalid number of participants", "negative")
        return redirect(url_for("occurrence_details", id=id))
    if not participants_number.isdigit():
        flash("Invalid number of participants", "negative")
        return redirect(url_for("occurrence_details", id=id))
    participants_number = int(participants_number)

    reserved_number= occurrencies_dao.get_participants_number(occurrence) + occurrencies_dao.get_extra_participants_number(occurrence)
    if participants_number > reserved_number or participants_number < 0:
        flash("Too high or low number of participants", "negative")
        return redirect(url_for("occurrence_details", id=id))
    
    # image validation
    report_image=request.files.get("reportImage", None)
    if report_image is None:
        flash("Report image is required", "negative")
        return redirect(url_for("occurrence_details", id=id))
    if images.is_image(report_image) == False:
        flash("The uploaded file is not an image", "negative")
        return redirect(url_for("occurrence_details", id=id))
    if images.is_16_9able(report_image) == False:
        flash(f"The uploaded photo is too small and cannot be resized to 16:9, minimum size is {TOUR_PHOTO_IMG_WIDTH}x{TOUR_PHOTO_IMG_HEIGHT}", "negative")
        return redirect(url_for("occurrence_details", id=id))
    
    extension=secure_filename(report_image.filename).split(".")[-1].lower()
    report_image_filename=str(uuid.uuid4()) + "." + extension
    report_image.filename = report_image_filename
    report_image = images.to_16_9(report_image)
    report_image.save("static/images/report_photos/" + report_image_filename)

    # report creation
    report_obj=Report(str(uuid.uuid4()), occurrence.id, participants_number, report_image_filename)
    if not reports_dao.add_report(report_obj):
        flash("An error occurred, report not created", "negative")
        return redirect(url_for("occurrence_details", id=id))
    
    logs_dao.add_log(f"Report created by user ID {current_user.id}")
    return redirect(url_for("occurrence_details", id=id))

# RESERVATIONS MANAGEMENT

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

    # create the occurrence only at the first reservation for this tour and date
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
    if participant_number + occurrencies_dao.get_participants_number(occurrence_obj) + occurrencies_dao.get_extra_participants_number(occurrence_obj) > tour.max_participants:
        flash("The number of participants exceeds the maximum allowed for this tour", "negative")
        return redirect(url_for("tour", id=id))

    participants= [first_participant, second_participant, third_participant]

    # participant_number includes current_user, so only the others are checked here
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
    logs_dao.add_log(f"Tour booked successfully by user ID {current_user.id}")
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
    logs_dao.add_log(f"Reservation canceled successfully by user ID {current_user.id}")
    return redirect(url_for("my_profile"))

@app.route("/reservations/<id>/calendar")
@login_required
@participant_required
def add_reservation_to_calendar(id):

    zone = ZoneInfo("Europe/Rome")
    
    #check ownership of the reservation
    reservation=reservations_dao.get_reservation_by_id(id)
    if reservation is None:
        flash("Reservation not found", "negative")
        return redirect(url_for("my_profile"))
    
    if reservation.participant_id != current_user.id:
        flash("You are not authorized to view this reservation", "negative")
        return redirect(url_for("my_profile"))
    
    reservation.occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
    reservation.occurrence.tour = tours_dao.get_tour_by_id(reservation.occurrence.tour_id)

    calendar = Calendar()
    event = Event()

    event.name = reservation.occurrence.tour.title
    start_datetime = datetime.combine(reservation.occurrence.date, datetime.strptime(reservation.occurrence.start_time, "%H:%M").time(), tzinfo=zone)
    end_datetime = start_datetime + timedelta(minutes=reservation.occurrence.tour.duration)
    event.begin = start_datetime
    event.end = end_datetime

    calendar.events.add(event)

    response = Response(calendar.serialize(), mimetype='text/calendar')

    return response

@app.route("/me/calendar")
@login_required
def my_calendar():

    calendar = Calendar()
    zone = ZoneInfo("Europe/Rome")

    if current_user.role == "guide":
        occurrences = occurrencies_dao.get_not_empty_occurrences_by_guide_id(current_user.id)
        for occurrence in occurrences:
            occurrence.tour = tours_dao.get_tour_by_id(occurrence.tour_id)
            occurrence.reservations = reservations_dao.get_active_reservations_by_occurrence_id(occurrence.id)

            event = Event()
            event.name = occurrence.tour.title
            start_datetime = datetime.combine(occurrence.date, datetime.strptime(occurrence.start_time, "%H:%M").time(), tzinfo=zone)
            end_datetime = start_datetime + timedelta(minutes=occurrence.tour.duration)
            event.begin = start_datetime
            event.end = end_datetime
            
            calendar.events.add(event)

    else:
        reservations = reservations_dao.get_active_reservations_by_participant_id(current_user.id)

        for reservation in reservations:
            reservation.occurrence = occurrencies_dao.get_occurrence_by_id(reservation.occurrence_id)
            reservation.occurrence.tour = tours_dao.get_tour_by_id(reservation.occurrence.tour_id)

            event = Event()
            event.name = reservation.occurrence.tour.title
            start_datetime = datetime.combine(reservation.occurrence.date, datetime.strptime(reservation.occurrence.start_time, "%H:%M").time(), tzinfo=zone)
            end_datetime = start_datetime + timedelta(minutes=reservation.occurrence.tour.duration)
            event.begin = start_datetime
            event.end = end_datetime

            calendar.events.add(event)

    response = Response(calendar.serialize(), mimetype='text/calendar')

    return response


# ADMIN MANAGEMENT

@app.route("/admin")
def admin_login():
    
    return render_template("admin_login.html")

@app.route("/admin", methods=["POST"])
def admin_login_post():

    username = request.form.get("username")
    password = request.form.get("password")

    if username in [None, ""]:
        flash("Invalid username", "negative")
        return redirect(url_for("admin_login"))
    if password in [None, ""]:
        flash("Invalid password", "negative")
        return redirect(url_for("admin_login"))
    
    admin = admins_dao.get_admin_by_username(username)
    if admin is None:
        flash("Wrong username or password", "negative")
        return redirect(url_for("admin_login"))
    if check_password_hash(admin["password"], password) == False:
        flash("Wrong username or password", "negative")
        return redirect(url_for("admin_login"))

    #logout the user from the normal profile
    if current_user.is_authenticated:
        logout_user()

    logs_dao.add_log("Admin login successful")

    return admin_dashboard(origin="admin_login", admin=admin)



@app.route("/admin/dashboard")
def admin_dashboard(origin=None, admin=None):

    if origin != "admin_login":
        flash("You must be logged in as admin to access this page", "negative")
        return redirect(url_for("admin_login"))
    
    admin = admins_dao.get_admin_by_username(admin["username"])
    if admin is None:
        flash("You must be logged in as admin to access this page", "negative")
        return redirect(url_for("admin_login"))

    # retrieve all informations
    participant_number = users_dao.count_users(role="participant")
    tour_number = tours_dao.count_tours(state="active")
    reservation_number = reservations_dao.count_reservations(state="active")

    languages = languages_dao.get_languages()
    themes = themes_dao.get_themes()

    for language in languages:
        language["reservations_number"] = reservations_dao.count_reservations_by_language_id(language["id"], state="active")
    
    for theme in themes:
        theme.reservations_number = reservations_dao.count_reservations_by_theme_id(theme.id, state="active")

    guides = users_dao.get_users(role="guide")
    for guide in guides:
        guide.languages = languages_dao.get_languages_by_user_id(guide.id)
        guide.tours = tours_dao.get_tours_by_guide_id(guide.id)
        for tour in guide.tours:
            tour.theme = themes_dao.get_theme_by_id(tour.theme_id)
            tour.photos = photos_dao.get_tour_photos(tour)
            tour.weekly_schedule = tours_dao.get_weekly_schedule_by_tour(tour)
            tour.stops = stops_dao.get_stops_by_tour(tour)
            tour.language = languages_dao.get_language_by_id(tour.language_id)["name"]
            

    logs = logs_dao.get_logs()

    return render_template("admin_dashboard.html", admin=admin, guides=guides, participants_number=participant_number, tour_number=tour_number, reservation_number=reservation_number, languages=languages, themes=themes, logs=logs)
