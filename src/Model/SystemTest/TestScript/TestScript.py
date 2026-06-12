class TestScript:

    def __init__(self, requirement_id: str, script_path: str, script_content: str = ''):
        self.set_requirement_id(requirement_id)
        self.set_script_path(script_path)
        self.set_script_content(script_content)

    def get_requirement_id(self) -> str: return self.__requirement_id
    def set_requirement_id(self, v: str): self.__requirement_id = v

    def get_script_path(self) -> str: return self.__script_path
    def set_script_path(self, v: str): self.__script_path = v

    def get_script_content(self) -> str: return self.__script_content
    def set_script_content(self, v: str): self.__script_content = v

    def load_content_from_file(self):
        with open(self.__script_path, 'r', encoding='utf-8') as f:
            self.__script_content = f.read()

    def save_content_to_file(self, new_content: str = None):
        content = new_content or self.__script_content
        with open(self.__script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        if new_content:
            self.__script_content = new_content
