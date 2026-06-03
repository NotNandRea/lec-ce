import re

def check_email(email):
    pattern="[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]+"

    if re.match(pattern,email):
        return True
    return False