from flask_login import UserMixin
from werkzeug.security import check_password_hash

class User(UserMixin):
    def __init__(self, id, role, email, password, first_name, last_name, profile_photo):
        self.id = id
        self.role = role
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.profile_photo = profile_photo

    def print_user(self):
        print(f"ID: {self.id}, Role: {self.role}, Email: {self.email}, First Name: {self.first_name}, Last Name: {self.last_name}, Profile Photo: {self.profile_photo}")
        return

    def check_password(self,string):
        return check_password_hash(self.password, string)