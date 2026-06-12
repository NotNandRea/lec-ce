class Reservation:
    def __init__(self, id, participant_id, occurrence_id, timestamp_booking, state=None):
        self.id = id
        self.participant_id = participant_id
        self.occurrence_id = occurrence_id
        self.occurrence = None
        self.timestamp_booking = timestamp_booking
        self.state = state