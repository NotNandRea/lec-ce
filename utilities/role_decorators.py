from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

def guide_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.role == "guide":
            flash("You must be a guide to access this page", "negative")
            return redirect(url_for("home"))

        return func(*args, **kwargs)
    return wrapper

def participant_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.role == "participant":
            flash("You must be a participant to access this page", "negative")
            return redirect(url_for("home"))

        return func(*args, **kwargs)
    return wrapper