
class FunctionalityNotExists(Exception):
    
    def __init__(self, message="Functionality not exists"):
        super().__init__(message)