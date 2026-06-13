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

def check_overlap(first_start_time, first_duration, second_start_time, second_duration):
    # Convert in minutes from 00:00
    first_hours = int(first_start_time.split(":")[0])
    first_minutes = int(first_start_time.split(":")[1])
    first_start_time_minutes = first_hours * 60 + first_minutes

    second_hours = int(second_start_time.split(":")[0])
    second_minutes = int(second_start_time.split(":")[1])
    second_start_time_minutes = second_hours * 60 + second_minutes

    first_end_time_minutes = first_start_time_minutes + first_duration
    second_end_time_minutes = second_start_time_minutes + second_duration

    if first_start_time_minutes < second_end_time_minutes and second_start_time_minutes < first_end_time_minutes:
        return True
    return False