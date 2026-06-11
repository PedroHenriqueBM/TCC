class DatasetNotExistsOnPath(Exception):

    def __init__(self, menssage="Usability Heuristic Dataset is missing on path setted"):
        super().__init__(menssage)