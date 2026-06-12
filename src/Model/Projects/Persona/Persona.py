class Persona:

    def __init__(self, id: str, project_id: str, name: str, opportunities: str = '',
                 key_attributes: str = '', description: str = '',
                 needs: str = '', challenges: str = ''):
        self.set_id(id)
        self.set_project_id(project_id)
        self.set_name(name)
        self.set_opportunities(opportunities)
        self.set_key_attributes(key_attributes)
        self.set_description(description)
        self.set_needs(needs)
        self.set_challenges(challenges)

    def get_id(self) -> str: return self.__id
    def set_id(self, v: str): self.__id = v

    def get_project_id(self) -> str: return self.__project_id
    def set_project_id(self, v: str): self.__project_id = v

    def get_name(self) -> str: return self.__name
    def set_name(self, v: str): self.__name = v

    def get_opportunities(self) -> str: return self.__opportunities
    def set_opportunities(self, v: str): self.__opportunities = v

    def get_key_attributes(self) -> str: return self.__key_attributes
    def set_key_attributes(self, v: str): self.__key_attributes = v

    def get_description(self) -> str: return self.__description
    def set_description(self, v: str): self.__description = v

    def get_needs(self) -> str: return self.__needs
    def set_needs(self, v: str): self.__needs = v

    def get_challenges(self) -> str: return self.__challenges
    def set_challenges(self, v: str): self.__challenges = v

    def to_summary(self) -> str:
        return (
            f"Persona: {self.__name}\n"
            f"  Descrição: {self.__description}\n"
            f"  Oportunidades: {self.__opportunities}\n"
            f"  Atributos-chave: {self.__key_attributes}\n"
            f"  Necessidades: {self.__needs}\n"
            f"  Desafios: {self.__challenges}"
        )

    @staticmethod
    def from_dict(data: dict) -> 'Persona':
        return Persona(
            id=data['id'],
            project_id=data['project_id'],
            name=data['name'],
            opportunities=data.get('opportunities', ''),
            key_attributes=data.get('key_attributes', ''),
            description=data.get('description', ''),
            needs=data.get('needs', ''),
            challenges=data.get('challenges', '')
        )
