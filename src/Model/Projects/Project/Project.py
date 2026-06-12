class Project:

    def __init__(self, id: str, name: str, description: str, status: str = 'active'):
        self.set_id(id)
        self.set_name(name)
        self.set_description(description)
        self.set_status(status)

    def get_id(self) -> str:
        return self.__id
    def set_id(self, new_id: str):
        self.__id = new_id

    def get_name(self) -> str:
        return self.__name
    def set_name(self, new_name: str):
        self.__name = new_name

    def get_description(self) -> str:
        return self.__description
    def set_description(self, new_description: str):
        self.__description = new_description

    def get_status(self) -> str:
        return self.__status
    def set_status(self, new_status: str):
        self.__status = new_status

    @staticmethod
    def from_dict(data: dict) -> 'Project':
        return Project(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            status=data.get('status', 'active')
        )
