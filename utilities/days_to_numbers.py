def days_to_numbers(tour):

    avaiable_days=" "

    for day in tour.weekly_schedule.keys():
        if tour.weekly_schedule[day] is not None:
            if day == "monday":
                avaiable_days += "1,"
            elif day == "tuesday":
                avaiable_days += "2,"
            elif day == "wednesday":
                avaiable_days += "3,"
            elif day == "thursday":
                avaiable_days += "4,"
            elif day == "friday":
                avaiable_days += "5,"
            elif day == "saturday":
                avaiable_days += "6,"
            elif day == "sunday":
                avaiable_days += "0,"
    
    avaiable_days = avaiable_days[:-1]

    return avaiable_days