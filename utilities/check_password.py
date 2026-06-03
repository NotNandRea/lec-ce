import re

def check_password(password):
    numbers="[0-9]+"# password must contain at least one number
    length=".{8,}" # password must contain at least 8 characters 
    letters="[A-Za-z]+" # password must contain at least one letter
    symbols="[!@#$%^&*()_+=-]+" # password must contain at least one symbol

    if re.search(numbers, password) and re.search(length, password) and re.search(letters, password) and re.search(symbols, password):
        return True
    return False