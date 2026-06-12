import uuid
from Model.Projects.FunctionalRequirement.FunctionalRequirement import FunctionalRequirement
from Model.Projects.ConformityAgents.FunctionalRequirementConformityAgent.FunctionalRequirementConformityAgent import FunctionalRequirementConformityAgent
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Database.repositories.project_repository import project_exists
from Database.repositories.functional_requirement_repository import (
    create_functional_requirement as db_create,
    link_persona_to_requirement
)


class FunctionalRequirementConformityError(Exception):
    def __init__(self, result: ConformityResult):
        self.result = result
        super().__init__(f"Requisito Funcional inválido: {result.feedback}")


class ProjectNotFoundError(Exception):
    pass


def create_functional_requirement(project_id: str, name: str, url: str = '',
                                   persona_ids: list[str] = None) -> FunctionalRequirement:
    """
    Cria um Requisito Funcional (formato ARO) em um Projeto. (3)
    - 3.1: Consulta política do agente
    - 3.2: Verifica se está no formato ARO
    """
    if not project_exists(project_id):
        raise ProjectNotFoundError(f"Projeto '{project_id}' não encontrado.")

    # 3.2 - Verifica formato ARO
    agent = FunctionalRequirementConformityAgent()
    result = agent.validate_name(name)

    if not result.valid:
        raise FunctionalRequirementConformityError(result)

    req_id = str(uuid.uuid4())
    db_create(id=req_id, project_id=project_id, name=name, url=url)

    if persona_ids:
        for pid in persona_ids:
            link_persona_to_requirement(requirement_id=req_id, persona_id=pid)

    return FunctionalRequirement(id=req_id, project_id=project_id, name=name, url=url)
