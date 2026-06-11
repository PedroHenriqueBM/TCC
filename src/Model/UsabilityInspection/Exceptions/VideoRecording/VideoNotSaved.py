

class VideoNotSaved(Exception):
    
    def __init__(self, menssage="Video was not saved"):
        super().__init__(menssage)