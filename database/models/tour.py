class Tour:
    def __init__(self, id, title, description, duration, max_participants, theme_id=None, language_id=None, guide_id=None, state=None):
        self.id = id
        self.title = title
        self.description = description
        self.duration = duration
        self.max_participants = max_participants
        self.state = state
        self.theme_id = theme_id
        self.theme = None
        self.language_id = language_id
        self.language = None
        self.guide_id = guide_id
        self.guide = None
        self.weekly_schedule = None
        self.photos = {"1": None, "2": None, "3": None, "4": None, "5": None}
        self.stops = None