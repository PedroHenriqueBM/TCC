class FunctionalRequirement:
    """
    Representa um Requisito Funcional no formato ARO (Ator + Requisito + Objeto).
    Exemplo: "O Tester executa Script de Teste"
    """

    def __init__(self, id: str, project_id: str, name: str, url: str = '',
                 acceptance_criteria: list = None, personas: list = None):
        self.set_id(id)
        self.set_project_id(project_id)
        self.set_name(name)
        self.set_url(url)
        self.__acceptance_criteria: list = acceptance_criteria or []
        self.__personas: list = personas or []

    def get_id(self) -> str: return self.__id
    def set_id(self, v: str): self.__id = v

    def get_project_id(self) -> str: return self.__project_id
    def set_project_id(self, v: str): self.__project_id = v

    def get_name(self) -> str: return self.__name
    def set_name(self, v: str): self.__name = v

    def get_url(self) -> str: return self.__url
    def set_url(self, v: str): self.__url = v

    def get_acceptance_criteria(self) -> list: return self.__acceptance_criteria
    def set_acceptance_criteria(self, v: list): self.__acceptance_criteria = v

    def get_personas(self) -> list: return self.__personas
    def set_personas(self, v: list): self.__personas = v

    def get_acceptance_criteria_as_text(self) -> str:
        if not self.__acceptance_criteria:
            return ""
        return "\n".join(
            f"- {ac.get('content', ac) if isinstance(ac, dict) else ac}"
            for ac in self.__acceptance_criteria
        )

    def get_personas_as_text(self) -> str:
        if not self.__personas:
            return ""
        lines = []
        for p in self.__personas:
            if isinstance(p, dict):
                lines.append(f"- {p.get('name', '')}: {p.get('description', '')}")
            else:
                lines.append(f"- {p}")
        return "\n".join(lines)

    @staticmethod
    def from_dict(data: dict) -> 'FunctionalRequirement':
        return FunctionalRequirement(
            id=data['id'],
            project_id=data['project_id'],
            name=data['name'],
            url=data.get('url', ''),
            acceptance_criteria=data.get('acceptance_criteria', []),
            personas=data.get('personas', [])
        )
