def check_time(string):
    if len(string) != 5 or string[2] != ":":
        return False
    hours = string.split(":")[0]
    minutes = string.split(":")[1]
    if not (hours.isdigit() and minutes.isdigit()):
        return False
    hours = int(hours)
    minutes = int(minutes)

    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        return False
    return True