class GameRetrievalException (ValueError):
    def __init__(self, message, status, error_type):
        self.message = message
        self.status = status
        self.error_type = error_type
