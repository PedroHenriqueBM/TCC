from Model.UsabilityInspection.Functionality.Functionality import Funcionality

def get_functionality_by_id(functionality_id: str):
    
    functionality = Funcionality("001","O sistema deve permitir que o usuário possa pesquisar coisas na internet","https://www.google.com/")

    return functionality