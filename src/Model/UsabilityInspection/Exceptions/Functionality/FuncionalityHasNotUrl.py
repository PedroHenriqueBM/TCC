
class FunctionalityHasNotUrl(Exception):
    
    def __init__(self, message="Functionality has not url"):
        super().__init__(message)