from functools import wraps

from flask_login import current_user
from database.models.user import User

#this decorator protects the guide reserved routes
def guide_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != "guide":
            return "Forbidden", 400
        return func(*args, **kwargs)
    return wrapper

#this decorator protects the participant reserved routes
def participant_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != "participant":
            return "Forbidden", 400
        return func(*args, **kwargs)
    return wrapper