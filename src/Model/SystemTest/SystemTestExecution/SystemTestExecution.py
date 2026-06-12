class SystemTestExecution:

    def __init__(self, id: str, requirement_id: str, passed: bool,
                 result_text: str = '', script_path: str = '', created_at: str = ''):
        self.set_id(id)
        self.set_requirement_id(requirement_id)
        self.set_passed(passed)
        self.set_result_text(result_text)
        self.set_script_path(script_path)
        self.set_created_at(created_at)

    def get_id(self) -> str: return self.__id
    def set_id(self, v: str): self.__id = v

    def get_requirement_id(self) -> str: return self.__requirement_id
    def set_requirement_id(self, v: str): self.__requirement_id = v

    def get_passed(self) -> bool: return self.__passed
    def set_passed(self, v: bool): self.__passed = v

    def get_result_text(self) -> str: return self.__result_text
    def set_result_text(self, v: str): self.__result_text = v

    def get_script_path(self) -> str: return self.__script_path
    def set_script_path(self, v: str): self.__script_path = v

    def get_created_at(self) -> str: return self.__created_at
    def set_created_at(self, v: str): self.__created_at = v

    @staticmethod
    def from_dict(data: dict) -> 'SystemTestExecution':
        return SystemTestExecution(
            id=data['id'],
            requirement_id=data['requirement_id'],
            passed=bool(data['passed']),
            result_text=data.get('result_text', ''),
            script_path=data.get('script_path', ''),
            created_at=data.get('created_at', '')
        )
