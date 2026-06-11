
import os

class UsabilityHeuristicDatabase:

    def __init__(self):
        self.file_name = "heuristic_dataset.json"

    def get_path_of_dataset(self):
        return os.path.join(
            os.getcwd(),"src","Model","UsabilityInspection","IntelligentUsabilityInspectionAgent","UsabilityHeuristicDatabase",self.file_name
        )
    def get_name_of_dataset(self):
        return self.file_name