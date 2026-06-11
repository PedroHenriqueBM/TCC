class Comment:

    def __init__(
            self,
            id: str,
            content: str,
            author: str,
            timestamp: str
    ):
        if id:
            self.set_id(id)
        self.set_content(content)
        self.set_author(author)
        self.set_timestamp(timestamp)

    def get_id(self):
        return self.__id
    def set_id(self, new_id: str):
        self.__id = new_id

    def get_content(self):
        return self.__content
    def set_content(self, new_content):
        self.__content = new_content

    def get_author(self):
        return self.__author
    def set_author(self,new_author):
        self.__author = new_author

    def get_timestamp(self):
        return self.__timestamp
    def set_timestamp(self, new_timestamp):
        self.__timestamp = new_timestamp