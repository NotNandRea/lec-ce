class Occurrence:
    def __init__(self, id, tour_id, date, start_time, tour=None, state=None):
        self.id = id
        self.tour_id = tour_id
        self.tour = tour
        self.date = date
        self.start_time = start_time
        self.state = state