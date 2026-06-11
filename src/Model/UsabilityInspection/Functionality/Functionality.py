from Model.UsabilityInspection.Functionality.Comment.Comment import Comment
from Model.UsabilityInspection.Functionality.AcceptanceCriteria.AcceptanceCriteria import AcceptanceCriteria

class Funcionality:

    def __init__(self, id: str, description: str, url: str):
        
        if id:
            self.set_id(id)
        self.set_description(description)
        self.set_url(url)
        self.__comments: list[Comment] = []
        self.__acceptance_criteria: list[AcceptanceCriteria] = []
    
    def get_id(self) -> str:
        return self.__id
    def set_id(self, new_id: str):
        self.__id = new_id

    def get_description(self) -> str:
        return self.__description
    def set_description(self, new_description: str):
        self.__description = new_description
    
    def get_url(self) -> str:
        return self.__url
    def set_url(self, new_url: str):
        self.__url = new_url

    def add_comment(self, id: str, description:str,author:str, timestamp: str):
        self.__comments.append(Comment(id,description,author,timestamp))

    def get_comments(self) -> str:
        
        final_text = ""
        for comment in self.__comments:
            final_text = final_text + f"{comment.get_id()} | {comment.get_content} | {comment.get_author()} | {comment.get_timestamp()}\n"
        return final_text

    def add_acceptance_criteria(self, id: str, description:str,author:str, timestamp: str):
        self.__acceptance_criteria.append(AcceptanceCriteria(id,description,author,timestamp))

    def get_acceptance_criteria(self) -> str:
        
        final_text = ""
        for acceptance_criteria in self.__acceptance_criteria:
            final_text = final_text + f"{acceptance_criteria.get_id()} | {acceptance_criteria.get_content} | {acceptance_criteria.get_author()} | {acceptance_criteria.get_timestamp()}\n"
        return final_text
