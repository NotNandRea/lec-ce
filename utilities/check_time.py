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

def check_week_overlap(day1, time1, duration1, day2, time2, duration2):
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    minutes_in_week = 7 * 1440

    hours1 = int(time1.split(":")[0])
    minutes1 = int(time1.split(":")[1])

    hours2 = int(time2.split(":")[0])
    minutes2 = int(time2.split(":")[1])

    # compute the start and end times in minutes since the beginning of the week
    minutes_start1 = days.index(day1) * 1440 + hours1 * 60 + minutes1
    minutes_end1 = minutes_start1 + duration1

    minutes_start2 = days.index(day2) * 1440 + hours2 * 60 + minutes2
    minutes_end2 = minutes_start2 + duration2

    #put the minutes in an interval
    intervals1 = [(minutes_start1, minutes_end1)]
    intervals2 = [(minutes_start2, minutes_end2)]

    # if the tour ends for example the monday after a sunday
    if minutes_end1 > minutes_in_week:
        # split the interval in two intervals, one in the current week and one in the next week
        intervals1 = [(minutes_start1, minutes_in_week), (0, minutes_end1 - minutes_in_week)]

    if minutes_end2 > minutes_in_week:
        intervals2 = [(minutes_start2, minutes_in_week), (0, minutes_end2 - minutes_in_week)]

    for s1, e1 in intervals1:
        for s2, e2 in intervals2:
            if s1 < e2 and s2 < e1:
                return True

    return False