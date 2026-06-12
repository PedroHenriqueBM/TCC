import json
from Model.Projects.ConformityAgents.ProjectConformityAgent.Policy import ProjectConformityPolicy
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client


class ProjectConformityAgent:

    def __init__(self):
        self.__policy = ProjectConformityPolicy()
        self.__client = get_openai_client()

    def __ask(self, user_prompt: str) -> ConformityResult:
        response = self.__client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.__policy.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        return ConformityResult(valid=bool(data.get("valid", False)), feedback=data.get("feedback", ""))

    def validate_name(self, name: str) -> ConformityResult:
        """Verifica se o nome do Projeto é válido. (1.3)"""
        prompt = (
            f"Valide se o nome de um Projeto de software está adequado.\n"
            f"Regras: deve ser não vazio, ter entre 3 e 100 caracteres, "
            f"ser descritivo e não conter palavras ofensivas.\n"
            f"Nome: \"{name}\""
        )
        return self.__ask(prompt)

    def validate_description(self, description: str) -> ConformityResult:
        """Verifica se a descrição do Projeto é válida. (1.2)"""
        prompt = (
            f"Valide se a descrição de um Projeto de software está adequada.\n"
            f"Regras: deve ser não vazia, ter entre 10 e 1000 caracteres, "
            f"descrever o objetivo do projeto de forma clara e não conter conteúdo inapropriado.\n"
            f"Descrição: \"{description}\""
        )
        return self.__ask(prompt)
