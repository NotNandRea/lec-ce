class Occurrence:
    def __init__(self, id, tour_id, date, start_time, state=None, tour=None, reservation=None):
        self.id = id
        self.tour_id = tour_id
        self.tour = tour
        self.date = date
        self.start_time = start_time
        self.state = state
        #IMPORTANT: this attribute is only used in loading the occurrences of a participant in his profile, since in this case an occurrence is linked to just a reservation we can use it like this
        self.reservation = reservation