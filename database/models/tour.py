class Tour:
    def __init__(self, id, guide_id, language_id, theme_id, title, description, meeting_point, duration, max_people):
        self.id = id
        self.guide_id = guide_id
        self.language_id = language_id
        self.theme_id = theme_id
        self.title = title
        self.description = description
        self.meeting_point = meeting_point
        self.duration = duration
        self.max_people = max_people