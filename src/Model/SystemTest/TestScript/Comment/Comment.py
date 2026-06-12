class Comment:

    def __init__(self, id: str, content: str, author: str, timestamp: str):
        self.set_id(id)
        self.set_content(content)
        self.set_author(author)
        self.set_timestamp(timestamp)

    def get_id(self) -> str: return self.__id
    def set_id(self, v: str): self.__id = v

    def get_content(self) -> str: return self.__content
    def set_content(self, v: str): self.__content = v

    def get_author(self) -> str: return self.__author
    def set_author(self, v: str): self.__author = v

    def get_timestamp(self) -> str: return self.__timestamp
    def set_timestamp(self, v: str): self.__timestamp = v
