class FunctionalityMissing(Exception):

    def __init__(self, message="Functionality is missing"):
        super().__init__(message)