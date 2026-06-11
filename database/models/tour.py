class Tour:
    def __init__(self, id, title, description, duration, max_participants):
        self.id = id
        self.title = title
        self.description = description
        self.duration = duration
        self.max_participants = max_participants
        self.photos = {"photo1": None, "photo2": None, "photo3": None, "photo4": None, "photo5": None}
        self.theme = None
        self.language = None
        self.guide = None
        self.weekly_schedule = {"monday": None, "tuesday": None, "wednesday": None, "thursday": None, "friday": None, "saturday": None, "sunday": None}
        self.stops = None

    def get_meeting_point(self):
        return self.stops[0]