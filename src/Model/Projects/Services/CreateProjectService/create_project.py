import uuid
from Model.Projects.Project.Project import Project
from Model.Projects.ConformityAgents.ProjectConformityAgent.ProjectConformityAgent import ProjectConformityAgent
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Database.repositories.project_repository import create_project as db_create_project


class ProjectConformityError(Exception):
    def __init__(self, results: list[ConformityResult]):
        self.results = results
        messages = [r.feedback for r in results if not r.valid]
        super().__init__("Projeto não atende aos critérios de conformidade: " + " | ".join(messages))


def create_project(name: str, description: str) -> Project:
    """
    Cria um Projeto após validação pelos agentes de conformidade. (1)
    - 1.1: Consulta política do agente
    - 1.2: Verifica se descrição é válida
    - 1.3: Verifica se nome é válido
    """
    agent = ProjectConformityAgent()

    # 1.3 - Verifica nome
    name_result = agent.validate_name(name)
    # 1.2 - Verifica descrição
    description_result = agent.validate_description(description)

    failures = [r for r in [name_result, description_result] if not r.valid]
    if failures:
        raise ProjectConformityError([name_result, description_result])

    project_id = str(uuid.uuid4())
    db_create_project(id=project_id, name=name, description=description)

    return Project(id=project_id, name=name, description=description)
